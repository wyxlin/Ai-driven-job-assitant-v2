from __future__ import annotations

import logging
import re

from sqlalchemy import select

from core.models import Job, get_session

logger = logging.getLogger(__name__)

# Seattle-area keywords — checked first via simple substring match
_LOCATION_KEYWORDS = [
    "greater seattle area",
    "seattle",
    "bellevue",
    "redmond",
    "kirkland",
    "renton",
    "eastside",
]

# "Remote" is handled separately: only US-based remote positions qualify
_US_STATES = frozenset({
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi",
    "missouri", "montana", "nebraska", "nevada", "new hampshire", "new jersey",
    "new mexico", "new york", "north carolina", "north dakota", "ohio",
    "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina",
    "south dakota", "tennessee", "texas", "utah", "vermont", "virginia",
    "washington", "west virginia", "wisconsin", "wyoming",
    "us", "usa", "united states", "district of columbia", "d.c.",
})

# Role filter: title must contain at least one allowlist term ...
_ROLE_ALLOWLIST = frozenset({"engineer", "developer", "swe"})

# ... and must NOT contain any blocklist term (above Senior level)
_ROLE_BLOCKLIST = frozenset({
    "staff", "principal", "lead", "director", "manager",
    "head", "architect", "scientist", "vp", "vice president",
})


def _has_us_remote(lower: str) -> bool:
    """Return True if any semicolon-separated segment is US-based remote."""
    for segment in re.split(r";", lower):
        segment = segment.strip()
        m = re.search(r"\bremote\s*-\s*(.+)", segment)
        if m:
            qualifier = m.group(1).strip()
            if any(state in qualifier for state in _US_STATES):
                return True
        elif "remote" in segment:
            return True
    return False


class FilterEngine:
    def is_location_match(self, location_str: str) -> bool:
        lower = location_str.lower()
        if any(kw in lower for kw in _LOCATION_KEYWORDS):
            return True
        if "remote" in lower:
            return _has_us_remote(lower)
        return False

    def is_role_match(self, title: str) -> bool:
        lower = title.lower()
        if any(blocked in lower for blocked in _ROLE_BLOCKLIST):
            return False
        return any(allowed in lower for allowed in _ROLE_ALLOWLIST)

    def run_filter_pass(self) -> None:
        with get_session() as session:
            jobs = (
                session.execute(select(Job).where(Job.is_filtered.is_(None)))
                .scalars()
                .all()
            )
            for job in jobs:
                location_ok = self.is_location_match(job.location or "")
                role_ok = self.is_role_match(job.title or "")
                job.is_filtered = location_ok and role_ok
                logger.debug(
                    "Job %s title=%r location=%r → is_filtered=%s",
                    job.id, job.title, job.location, job.is_filtered,
                )
