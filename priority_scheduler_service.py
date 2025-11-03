"""
Priority scheduler service.

This service provides a simplistic implementation of a job scheduler that
assigns pending jobs to available GPUs.  Jobs are processed in the
order they were created and assigned to the first GPU that is
available.  When a job is scheduled, its status is updated to
``running`` and the associated GPU is marked as unavailable.  In a
production system this would be replaced with a sophisticated
scheduler that considers job priorities, GPU capabilities and
throughput optimisation algorithms【398916126507635†L65-L75】.  This service lays the
groundwork for such an extension by demonstrating how jobs and GPUs
can be coordinated.
"""

from __future__ import annotations

from typing import List, Dict

from sqlalchemy.orm import Session

from backend.models.job import Job, JobStatus
from backend.models.gpu import GPU


class PrioritySchedulerService:
    """Service that assigns jobs to GPUs in a simple FIFO manner."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def run_scheduler(self) -> List[Dict[str, int]]:
        """Assign pending jobs to available GPUs.

        Returns
        -------
        List[Dict[str, int]]
            A list of assignments where each item contains a ``job_id`` and
            ``gpu_id`` indicating that the job has been scheduled on the
            specified GPU.
        """
        assignments: List[Dict[str, int]] = []
        # Get all pending jobs ordered by creation time (FIFO)
        pending_jobs = (
            self.db.query(Job)
            .filter(Job.status == JobStatus.PENDING.value)
            .order_by(Job.created_at.asc())
            .all()
        )
        # Get all available GPUs
        available_gpus = (
            self.db.query(GPU)
            .filter(GPU.is_available == True)
            .all()
        )
        # Convert GPU list to a set we can pop from
        gpu_pool = available_gpus.copy()
        for job in pending_jobs:
            if not gpu_pool:
                # No GPUs left; break early
                break
            # Pop the first available GPU
            gpu = gpu_pool.pop(0)
            # Assign job
            job.gpu_id = gpu.id
            job.status = JobStatus.RUNNING.value
            gpu.is_available = False
            assignments.append({"job_id": job.id, "gpu_id": gpu.id})
        # Persist changes
        self.db.commit()
        return assignments