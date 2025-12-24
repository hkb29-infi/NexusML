from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid

from backend.database import get_db
from backend.schemas.job import JobCreate, JobResponse, JobUpdate
from backend.services import job_service
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter()

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a new training job.
    
    Example request body:
    {
        "name": "ResNet50 Training",
        "config": {
            "model": "resnet50",
            "dataset": "imagenet",
            "epochs": 100,
            "batch_size": 256,
            "learning_rate": 0.1,
            "optimizer": "sgd"
        },
        "gpu_count": 1,
        "memory_gb": 16
    }
    """
    # Create job in database
    job = job_service.create_job(db, job_data, current_user.id)
    
    # Add to execution queue (background task)
    background_tasks.add_task(job_service.enqueue_job, job.id)
    
    return job

@router.get("/", response_model=List[JobResponse])
def list_jobs(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all jobs for the current user."""
    jobs = job_service.get_user_jobs(
        db, 
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status_filter=status
    )
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific job."""
    job = job_service.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a running or queued job."""
    job = job_service.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if job.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Job already finished")
    
    job_service.cancel_job(db, job_id)
    return None

@router.get("/{job_id}/metrics")
def get_job_metrics(
    job_id: uuid.UUID,
    metric_name: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get training metrics for a job."""
    job = job_service.get_job(db, job_id)
    
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    metrics = job_service.get_job_metrics(db, job_id, metric_name)
    return {"job_id": str(job_id), "metrics": metrics}
