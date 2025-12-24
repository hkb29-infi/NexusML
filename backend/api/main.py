from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from backend.database import get_db, engine
from backend.models import Base
from backend.api.routes import jobs, auth, experiments, metrics
from backend.core.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NexusML API",
    description="Distributed ML Training Platform",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(metrics.router, tags=["metrics"])

 @app.get("/")
def read_root():
    return {"message": "NexusML API", "version": "0.1.0"}

 @app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
