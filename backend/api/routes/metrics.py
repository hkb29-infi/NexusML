from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from backend.database import get_db
from backend.schemas.metric import MetricCreate
from backend.services import metric_service
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter()

@router.post("/api/jobs/{job_id}/metrics", status_code=status.HTTP_201_CREATED)
def create_metric_for_job(
    job_id: uuid.UUID,
    metric_data: MetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new metric for a job.
    """
    # TODO: check if user has access to the job
    metric = metric_service.create_metric(db, job_id, metric_data)
    return metric
