from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from ..services.github_service import (
    get_repo_info, get_repo_contents, read_file_content,
    get_directory_tree, analyze_complexity,
    get_dependencies, get_commit_history
)
from ..services.ai_service import get_code_explanation, chat_with_repo
from ..services.repo_context_service import extract_repo_summary, format_repo_context_for_prompt

router = APIRouter(prefix="/repo")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

class ChatRequest(BaseModel):
    query: str
    context: Dict[str, str] = {}
    repo_owner: Optional[str] = None
    repo_name: Optional[str] = None

class CodeExplanationRequest(BaseModel):
    code: str
    path: str

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "static": lambda path: f"/static/{path}"
        }
    )

@router.get("/{owner}/{repo}")
async def get_repository(request: Request, owner: str, repo: str):
    repo_info = get_repo_info(owner, repo)
    if isinstance(repo_info, tuple):
        raise HTTPException(status_code=repo_info[1], detail=repo_info[0])
    return templates.TemplateResponse(
        "repository.html",
        {
            "request": request,
            "repo": repo_info,
            "static": lambda path: f"/static/{path}"
        }
    )

@router.get("/{owner}/{repo}/contents/{file_path:path}")
async def get_file_content(owner: str, repo: str, file_path: str):
    content = read_file_content(owner, repo, file_path)
    
    if content is None:
        raise HTTPException(status_code=404, detail="File not found or unable to read")
    
    # Check if it's a binary file (returns a dict with metadata)
    if isinstance(content, dict) and content.get('is_binary'):
        return content  # Return metadata for binary files
    
    # Return text content
    return {"content": content}

# Add a route to proxy binary files (optional enhancement)
@router.get("/{owner}/{repo}/binary/{file_path:path}")
async def get_binary_file(owner: str, repo: str, file_path: str):
    """Proxy binary file content from GitHub"""
    content_info = read_file_content(owner, repo, file_path)
    
    if content_info is None or not isinstance(content_info, dict):
        raise HTTPException(status_code=404, detail="File not found")
    
    if not content_info.get('download_url'):
        raise HTTPException(status_code=404, detail="No download URL available for this file")
    
    # For security and performance, redirect to the GitHub raw content URL
    # rather than proxying the binary content through our server
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=content_info['download_url'])

@router.get("/{owner}/{repo}/contents/{path:path}")
async def list_contents(owner: str, repo: str, path: str = ""):
    return get_repo_contents(owner, repo, path)

@router.get("/{owner}/{repo}/tree")
async def get_tree(owner: str, repo: str):
    return get_directory_tree(owner, repo)

@router.get("/{owner}/{repo}/analyze")
async def analyze_repository(owner: str, repo: str):
    complexity = analyze_complexity(owner, repo)
    dependencies = get_dependencies(owner, repo)
    return {
        "complexity": complexity,
        "dependencies": dependencies
    }

@router.get("/{owner}/{repo}/history")
async def get_history(owner: str, repo: str):
    return get_commit_history(owner, repo)

@router.get("/{owner}/{repo}/context")
async def get_repo_context(owner: str, repo: str):
    """Get preloaded repository context for chat"""
    try:
        repo_summary = extract_repo_summary(owner, repo)
        repo_context = format_repo_context_for_prompt(repo_summary)
        
        return {
            "context": repo_context,
            "summary": {
                "top_level_dirs": repo_summary.get("top_level_dirs", []),
                "languages": repo_summary.get("languages", {}),
                "key_files": repo_summary.get("key_files", [])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain")
async def explain_code_route(request: CodeExplanationRequest):
    explanation = get_code_explanation(request.code, request.path)
    return {"text": explanation}

@router.get("/debug", response_class=HTMLResponse)
async def debug_page(request: Request):
    """Debug page for testing chat functionality"""
    return templates.TemplateResponse(
        "debug.html",
        {
            "request": request,
            "static": lambda path: f"/static/{path}"
        }
    )

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        print(f"Chat request received: query='{request.query}', repo={request.repo_owner}/{request.repo_name}")
        
        # Always check file content size
        if 'content' in request.context and request.context['content']:
            file_path = request.context.get('path', 'unknown file')
            content_length = len(request.context['content'])
            
            # For all files over 10KB, add file size info
            if content_length > 10000:
                print(f"Large file detected: {file_path} ({content_length} chars)")
                
            # For very large files, automatically truncate
            if content_length > 50000:
                print(f"Warning: Very large file content ({content_length} chars) for {file_path}")
                from ..services.ai_service import truncate_large_text
                request.context['content'] = truncate_large_text(
                    request.context['content'], 
                    request.context.get('path', '')
                )
        
        # Get repo tree and README summary if repo info is provided
        repo_tree = None
        readme_summary = ""
        repo_context = ""
        
        if request.repo_owner and request.repo_name:
            # Use the repo_context_service to get comprehensive repository context
            try:
                repo_summary = extract_repo_summary(request.repo_owner, request.repo_name)
                repo_context = format_repo_context_for_prompt(repo_summary)
                print(f"Repository context generated for {request.repo_owner}/{request.repo_name}")
            except Exception as e:
                print(f"Error getting repository context: {str(e)}")
        
        response = await chat_with_repo(
            query=request.query,
            code_context=request.context.get('content', ''),
            file_path=request.context.get('path', ''),
            repo_owner=request.repo_owner,
            repo_name=request.repo_name,
            repo_context=repo_context
        )
        
        if not response:
            print("AI service returned empty response")
            raise HTTPException(status_code=500, detail="No response from AI service")
            
        print(f"Chat response generated: {response[:50]}...")
        return {"text": response}
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
