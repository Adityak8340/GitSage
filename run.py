from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import repo_routes, analysis_routes
import uvicorn
from pathlib import Path

app = FastAPI()

# Configure static files
static_dir = Path(__file__).parent / "app" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Ensure the static directory exists
if not static_dir.exists():
    raise FileNotFoundError(f"Static directory not found: {static_dir}")

# Configure templates with context processor
templates = Jinja2Templates(directory=str(Path(__file__).parent / "app" / "templates"))

# Add context processor for static files
@app.middleware("http")
async def add_static_utilities(request: Request, call_next):
    async def static(path: str) -> str:
        return request.url_for("static", path=path)
    
    request.state.static = static
    response = await call_next(request)
    return response

# Make static function available to templates
templates.env.globals["static"] = lambda path: f"/static/{path}"

# Include routers
app.include_router(repo_routes.router)
app.include_router(analysis_routes.router)

if __name__ == '__main__':
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)