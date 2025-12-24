import redis
import json
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from backend.models.job import Job
from backend.schemas.job import JobCreate, JobUpdate

class JobService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=True
        )
    
    def create_job(self, db: Session, job_data: JobCreate, user_id: uuid.UUID) -> Job:
        """Create a new job in database."""
        job = Job(
            user_id=user_id,
            name=job_data.name,
            config=job_data.config,
            status="queued",
            priority=job_data.priority,
            gpu_count=job_data.gpu_count,
            memory_gb=job_data.memory_gb
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    
    def enqueue_job(self, job_id: uuid.UUID):
        """Add job to Redis queue for execution."""
        # Use sorted set for priority queue
        # Score = (priority * -1000000) + timestamp
        # This ensures higher priority jobs are processed first
        import time
        job_data = self.get_job(db, job_id)
        score = -job_data.priority * 1000000 + time.time()
        
        self.redis_client.zadd(
            "job_queue",
            {str(job_id): score}
        )
    
    def get_job(self, db: Session, job_id: uuid.UUID) -> Optional[Job]:
        """Get job by ID."""
        return db.query(Job).filter(Job.id == job_id).first()
    
    def get_user_jobs(
        self,
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None
    ) -> List[Job]:
        """Get all jobs for a user."""
        query = db.query(Job).filter(Job.user_id == user_id)
        
        if status_filter:
            query = query.filter(Job.status == status_filter)
        
        return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_job(self, db: Session, job_id: uuid.UUID, update_data: JobUpdate) -> Job:
        """Update job details."""
        job = self.get_job(db, job_id)
        if not job:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(job, key, value)
        
        db.commit()
        db.refresh(job)
        return job
    
    def cancel_job(self, db: Session, job_id: uuid.UUID) -> bool:
        """Cancel a job."""
        job = self.get_job(db, job_id)
        if not job:
            return False
        
        if job.status in ["queued"]:
            # Remove from Redis queue
            self.redis_client.zrem("job_queue", str(job_id))
        
        job.status = "cancelled"
        db.commit()
        return True
    
    def get_job_metrics(
        self,
        db: Session,
        job_id: uuid.UUID,
        metric_name: Optional[str] = None
    ) -> dict:
        """Get metrics for a job."""
        from backend.models.job import Metric
        
        query = db.query(Metric).filter(Metric.job_id == job_id)
        
        if metric_name:
            query = query.filter(Metric.metric_name == metric_name)
        
        metrics = query.order_by(Metric.timestamp).all()
        
        # Group by metric name
        result = {}
        for metric in metrics:
            if metric.metric_name not in result:
                result[metric.metric_name] = []
            
            result[metric.metric_name].append({
                "step": metric.step,
                "value": metric.metric_value,
                "timestamp": metric.timestamp.isoformat()
            })
        
        return result

job_service = JobService()
