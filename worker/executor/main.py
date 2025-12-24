import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime

import redis
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobExecutor:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        self.api_url = os.getenv("API_URL", "http://backend:8000")
        self.workspace = Path("/workspace/jobs")
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    def poll_jobs(self):
        """Poll Redis queue for new jobs."""
        while True:
            # Blocking pop from queue
            job_data = self.redis_client.blpop("job_queue", timeout=5)
            
            if job_data:
                _, job_id = job_data
                logger.info(f"Received job: {job_id}")
                self.execute_job(job_id)
    
    def execute_job(self, job_id: str):
        """Execute a training job."""
        try:
            # Fetch job details from API
            response = requests.get(f"{self.api_url}/api/jobs/{job_id}")
            job_data = response.json()
            
            # Update status to running
            self.update_job_status(job_id, "running", started_at=datetime.utcnow().isoformat())
            
            # Create job workspace
            job_dir = self.workspace / job_id
            job_dir.mkdir(exist_ok=True)
            
            # Write config file
            config_path = job_dir / "config.json"
            with open(config_path, 'w') as f:
                json.dump(job_data['config'], f, indent=2)
            
            # Generate training script from template
            script_path = self.generate_training_script(job_data, job_dir)
            
            # Execute training
            logger.info(f"Starting training for job {job_id}")
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=job_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Job {job_id} completed successfully")
                self.update_job_status(
                    job_id,
                    "completed",
                    completed_at=datetime.utcnow().isoformat(),
                    output_path=str(job_dir / "output")
                )
            else:
                logger.error(f"Job {job_id} failed: {result.stderr}")
                self.update_job_status(
                    job_id,
                    "failed",
                    completed_at=datetime.utcnow().isoformat(),
                    error_message=result.stderr
                )
        
        except Exception as e:
            logger.error(f"Error executing job {job_id}: {str(e)}")
            self.update_job_status(
                job_id,
                "failed",
                completed_at=datetime.utcnow().isoformat(),
                error_message=str(e)
            )
    
    def generate_training_script(self, job_data: dict, job_dir: Path) -> Path:
        """Generate training script from template."""
        config = job_data['config']
        
        # Load template
        template_path = Path("/workspace/templates/pytorch_template.py")
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Fill in config values
        script_content = template.format(
            model=config['model'],
            dataset=config['dataset'],
            epochs=config['epochs'],
            batch_size=config['batch_size'],
            learning_rate=config['learning_rate'],
            optimizer=config['optimizer'],
            job_id=job_data['id']
        )
        
        # Write script
        script_path = job_dir / "train.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return script_path
    
    def update_job_status(self, job_id: str, status: str, **kwargs):
        """Update job status via API."""
        update_data = {"status": status, **kwargs}
        requests.patch(
            f"{self.api_url}/api/jobs/{job_id}",
            json=update_data
        )

if __name__ == "__main__":
    executor = JobExecutor()
    logger.info("Job executor started, polling for jobs...")
    executor.poll_jobs()
