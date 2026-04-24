from __future__ import annotations

import logging
from typing import Optional

import config
from core.models import Job, JobEvaluation, LLMStatus, Resume, get_pending_jobs, get_session
from services.router import LLMRouter

logger = logging.getLogger(__name__)


class VettingService:
    def __init__(self, router: Optional[LLMRouter] = None) -> None:
        self.router = router or LLMRouter()

    def process_batch(self, batch_size: int = config.MAX_JOBS_PER_RUN) -> int:
        """Evaluate up to *batch_size* pending jobs. Returns count of jobs processed.

        Hard-capped at MAX_JOBS_PER_RUN (safety brake).
        """
        effective_limit = min(batch_size, config.MAX_JOBS_PER_RUN)

        resume = self._load_resume()
        if resume is None:
            logger.error("No resume found in DB; aborting vetting batch")
            return 0

        jobs = get_pending_jobs(effective_limit)
        if not jobs:
            logger.info("No pending jobs to vet")
            return 0

        logger.info("Vetting %d job(s) (cap=%d)", len(jobs), effective_limit)
        processed = 0
        for job in jobs:
            self._vet_one(job, resume)
            processed += 1

        logger.info("Vetting complete: %d job(s) processed", processed)
        return processed

    def _load_resume(self) -> Optional[dict]:
        with get_session() as session:
            row = session.query(Resume).order_by(Resume.id.desc()).first()
            return row.structured_data if row is not None else None

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
