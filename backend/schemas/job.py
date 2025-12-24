from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

class JobConfig(BaseModel):
    model: str
    dataset: str
    epochs: int
    batch_size: int
    learning_rate: float
    optimizer: str = "adam"
    # Add more fields as needed

class JobCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    config: Dict[str, Any]
    gpu_count: int = Field(default=1, ge=1, le=8)
    memory_gb: int = Field(default=16, ge=8, le=128)
    priority: int = Field(default=0, ge=0, le=10)

class JobUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class JobResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    status: str
    priority: int
    config: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    gpu_count: int
    memory_gb: int
    
    class Config:
        from_attributes = True
