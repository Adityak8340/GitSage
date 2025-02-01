from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import requests
from app.config import Config
from typing import Callable

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Add static function to template context
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "static": lambda path: f"/static/{path}"
        }
    )

@router.get("/repo/{owner}/{repo}")
async def repo_overview(request: Request, owner: str, repo: str):
    headers = {'Authorization': f'token {Config.GITHUB_TOKEN}'}
    repo_url = f'https://api.github.com/repos/{owner}/{repo}'
    
    repo_info = requests.get(repo_url, headers=headers).json()
    return templates.TemplateResponse("dashboard.html", {"request": request, "repo": repo_info})

@router.get("/api/files/{owner}/{repo}")
async def get_files(owner: str, repo: str):
    return {"files": []}