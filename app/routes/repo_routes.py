from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel

from ..services.github_service import (
    get_repo_info, get_repo_contents, read_file_content,
    get_directory_tree, analyze_complexity,
    get_dependencies, get_commit_history
)
from ..services.ai_service import get_code_explanation, chat_with_repo

router = APIRouter(prefix="/repo")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

class ChatRequest(BaseModel):
    query: str
    context: Dict[str, str] = {}

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
    return {"content": content}

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

@router.post("/explain")
async def explain_code_route(request: CodeExplanationRequest):
    explanation = get_code_explanation(request.code, request.path)
    return {"text": explanation}

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = await chat_with_repo(
            query=request.query,
            code_context=request.context.get('content', ''),
            file_path=request.context.get('path', '')
        )
        if not response:
            raise HTTPException(status_code=500, detail="No response from AI service")
        return {"text": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
