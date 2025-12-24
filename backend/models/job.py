from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from backend.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="queued")
    priority = Column(Integer, default=0)
    config = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    error_message = Column(Text, nullable=True)
    output_path = Column(Text, nullable=True)
    metrics = Column(JSON, nullable=True)
    
    gpu_count = Column(Integer, default=1)
    memory_gb = Column(Integer, default=16)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    metrics_history = relationship("Metric", back_populates="job", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="job", cascade="all, delete-orphan")

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    step = Column(Integer)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    
    job = relationship("Job", back_populates="metrics_history")
