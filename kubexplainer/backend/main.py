"""
Main FastAPI application for Kubernetes YAML Explainer.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.database import init_db
from app.routes import yaml_router, settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    # Create data directory if it doesn't exist
    os.makedirs("./data", exist_ok=True)
    
    # Initialize database
    await init_db()
    print("✓ Database initialized")
    
    yield
    
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Kubernetes YAML Explainer API",
    description="API for parsing, validating, and explaining Kubernetes YAML manifests",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(yaml_router)
app.include_router(settings_router)


@app.get("/api")
async def root():
    """API root endpoint."""
    return {
        "name": "Kubernetes YAML Explainer API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve frontend static files - must be last to not override API routes
if os.path.exists("./frontend/build"):
    @app.get("/")
    async def serve_frontend():
        """Serve the React frontend."""
        return FileResponse("./frontend/build/index.html")
    
    # Mount static assets
    app.mount("/static", StaticFiles(directory="./frontend/build/static"), name="static")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
