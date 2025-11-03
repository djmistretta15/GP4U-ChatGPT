"""
AI-driven scheduler service (placeholder).

This service demonstrates how an intelligent scheduler might assign
pending jobs to GPUs based on rudimentary heuristics.  In this
implementation jobs are sorted by creation time, and GPUs are scored
by a simple metric combining available memory and price; the job is
assigned to the GPU with the highest score.  In a production system
this service could incorporate machine-learning models that predict
job runtimes and GPU performance characteristics【398916126507635†L126-L133】.
"""

from __future__ import annotations

from typing import List, Dict

from sqlalchemy.orm import Session

from backend.models.job import Job, JobStatus
from backend.models.gpu import GPU


class AISchedulerService:
    """Service implementing a simple heuristic for assigning jobs to GPUs."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def run_ai_scheduler(self) -> List[Dict[str, int]]:
        """Assign pending jobs to GPUs using a simple scoring heuristic.

        Jobs are processed in FIFO order.  Each available GPU is scored
        using a heuristic that prefers higher memory and lower price.
        The job is assigned to the highest‑scoring GPU.  Once a GPU is
        assigned it becomes unavailable.  This method persists changes
        and returns a list of job→GPU assignments.

        Returns
        -------
        List[Dict[str, int]]
            A list of assignments (``job_id`` → ``gpu_id``).
        """
        assignments: List[Dict[str, int]] = []
        pending_jobs = (
            self.db.query(Job)
            .filter(Job.status == JobStatus.PENDING.value)
            .order_by(Job.created_at.asc())
            .all()
        )
        # Fetch all available GPUs
        available_gpus = (
            self.db.query(GPU)
            .filter(GPU.is_available == True)
            .all()
        )
        for job in pending_jobs:
            if not available_gpus:
                break
            # Score GPUs: memory_gb / price_per_hour; avoid division by zero
            best_gpu = None
            best_score = -1.0
            for gpu in available_gpus:
                price = gpu.price_per_hour or 0.01
                mem = gpu.memory_gb or 1
                score = (mem / price)
                if score > best_score:
                    best_score = score
                    best_gpu = gpu
            if best_gpu is None:
                break
            # Assign job
            job.gpu_id = best_gpu.id
            job.status = JobStatus.RUNNING.value
            best_gpu.is_available = False
            assignments.append({"job_id": job.id, "gpu_id": best_gpu.id})
            # Remove GPU from available pool
            available_gpus.remove(best_gpu)
        self.db.commit()
        return assignments