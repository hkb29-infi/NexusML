from pydantic import BaseModel
from datetime import datetime

class MetricCreate(BaseModel):
    step: int
    metric_name: str
    metric_value: float
    timestamp: datetime
