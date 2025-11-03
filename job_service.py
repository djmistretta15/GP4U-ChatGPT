"""
Job service layer.

This service provides operations for creating, retrieving and updating
jobs.  It does not implement actual job execution; scheduling and
execution would be handled by an external system or asynchronous
worker in a production environment.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.models.job import Job, JobStatus
from backend.models.gpu import GPU
from backend.models.user import User


class JobService:
    """Service for job management."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_job(self, *, user_id: int, gpu_id: int, command: str) -> Job:
        """Create a new job in pending state."""
        # Ensure user and GPU exist
        user = self.db.query(User).get(user_id)
        gpu = self.db.query(GPU).get(gpu_id)
        if not user:
            raise ValueError("Invalid user_id")
        if not gpu:
            raise ValueError("Invalid gpu_id")
        job = Job(user_id=user_id, gpu_id=gpu_id, command=command)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def list_jobs(self) -> List[Job]:
        """Return all jobs."""
        return self.db.query(Job).order_by(Job.created_at.desc()).all()

    def get_job(self, job_id: int) -> Optional[Job]:
        """Return a job by ID, or None if not found."""
        return self.db.query(Job).get(job_id)

    def start_job(self, job_id: int) -> Job:
        """Mark a job as running if it is pending."""
        job = self.db.query(Job).get(job_id)
        if not job:
            raise ValueError("Job not found")
        if job.status != JobStatus.PENDING.value:
            raise ValueError("Job is not pending")
        job.status = JobStatus.RUNNING.value
        job.started_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(job)
        return job

    def complete_job(self, job_id: int) -> Job:
        """Mark a job as completed if it is running."""
        job = self.db.query(Job).get(job_id)
        if not job:
            raise ValueError("Job not found")
        if job.status != JobStatus.RUNNING.value:
            raise ValueError("Job is not running")
        job.status = JobStatus.COMPLETED.value
        job.ended_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(job)
        return job