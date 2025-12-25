from sqlalchemy.orm import Session
import uuid

from backend.models.job import Metric
from backend.schemas.metric import MetricCreate

class MetricService:
    def create_metric(self, db: Session, job_id: uuid.UUID, metric_data: MetricCreate) -> Metric:
        metric = Metric(
            job_id=job_id,
            step=metric_data.step,
            metric_name=metric_data.metric_name,
            metric_value=metric_data.metric_value,
            timestamp=metric_data.timestamp
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

metric_service = MetricService()
