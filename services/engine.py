from __future__ import annotations

import logging

from sqlalchemy import select

from core.models import Job, get_session

logger = logging.getLogger(__name__)

# Longer phrases first so substring checks don't short-circuit on partial matches
_LOCATION_KEYWORDS = [
    "greater seattle area",
    "seattle",
    "bellevue",
    "redmond",
    "kirkland",
    "renton",
    "eastside",
    "remote",
]


class FilterEngine:
    def is_location_match(self, location_str: str) -> bool:
        lower = location_str.lower()
        return any(kw in lower for kw in _LOCATION_KEYWORDS)

    def run_filter_pass(self) -> None:
        with get_session() as session:
            jobs = (
                session.execute(select(Job).where(Job.is_filtered.is_(None)))
                .scalars()
                .all()
            )
            for job in jobs:
                job.is_filtered = self.is_location_match(job.location or "")
                logger.debug(
                    "Job %s location=%r → is_filtered=%s",
                    job.id,
                    job.location,
                    job.is_filtered,
                )
