from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import Config

def create_app():
    app = FastAPI(title="GitSage", description="GitHub Repository Analysis Tool")
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register error handlers
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"error": "Not found"}
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
    
    # Load config
    app.state.config = Config
    
    # Register routers (will be included in run.py)
    
    return app
