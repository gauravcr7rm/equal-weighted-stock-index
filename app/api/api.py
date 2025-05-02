from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.index import router as index_router
from app.api.routes.export import router as export_router
from app.core.config import settings

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title="Equal-Weighted Stock Index Tracker",
        description="A backend service that tracks and manages a custom equal-weighted stock index",
        version="1.0.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(index_router, tags=["Index"])
    app.include_router(export_router, tags=["Export"])
    
    # Add root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint to check if the API is running."""
        return {"message": "Equal-Weighted Stock Index Tracker API is running"}
    
    return app

# Create the FastAPI application
app = create_app()
