from __future__ import annotations

import logging
from typing import Optional

from core.models import Job, JobEvaluation, LLMStatus, get_pending_jobs, get_session
from services.router import LLMRouter

logger = logging.getLogger(__name__)


class VettingService:
    def __init__(self, router: Optional[LLMRouter] = None) -> None:
        self.router = router or LLMRouter()

    def run(self, resume: dict, limit: int = 100) -> int:
        """Evaluate pending jobs against *resume*. Returns count of jobs processed."""
        jobs = get_pending_jobs(limit)
        if not jobs:
            logger.info("No pending jobs to vet")
            return 0

        logger.info("Vetting %d job(s)", len(jobs))
        processed = 0
        for job in jobs:
            self._vet_one(job, resume)
            processed += 1

        logger.info("Vetting complete: %d job(s) processed", processed)
        return processed

    def _vet_one(self, job: Job, resume: dict) -> None:
        result = self.router.evaluate(resume, job.description or "")
        with get_session() as session:
            # job is detached (expunged by get_pending_jobs); re-fetch inside session
            live_job = session.get(Job, job.id)
            if live_job is None:
                logger.warning("Job id=%s not found during vetting save", job.id)
                return

            if result is None:
                live_job.llm_status = LLMStatus.failed
                logger.error("Job id=%s evaluation failed (all providers exhausted)", job.id)
            else:
                live_job.llm_status = LLMStatus.processed
                session.add(
                    JobEvaluation(
                        job_id=live_job.id,
                        match_score=result["match_score"],
                        reasoning=result["reasoning"],
                        model_used=result["model_used"],
                    )
                )
                logger.info(
                    "Job id=%s score=%s model=%s",
                    job.id,
                    result["match_score"],
                    result["model_used"],
                )
