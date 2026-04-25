from __future__ import annotations

import logging
from html.parser import HTMLParser
from typing import List

import requests

from core.models import upsert_jobs

logger = logging.getLogger(__name__)

# Companies to pull from Greenhouse. Add/remove slugs freely.
_GREENHOUSE_SLUGS = [
    "databricks",    # distributed systems / data engineering
    "anthropic",     # AI infrastructure
    "scaleai",       # AI / ML infrastructure
    "stripe",        # backend / distributed systems
    "smartsheet",    # Seattle-based, engineering roles
]


class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: List[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts).strip()


def _strip_html(html: str) -> str:
    s = _HTMLStripper()
    s.feed(html or "")
    return s.get_text()


def _fetch_greenhouse(company_slug: str) -> List[dict]:
    url = (
        f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
        "?content=true"
    )
    try:
        resp = requests.get(url, timeout=15)
    except requests.RequestException as exc:
        logger.warning("Greenhouse %s request failed: %s", company_slug, exc)
        return []

    if not resp.ok:
        logger.warning("Greenhouse %s returned HTTP %s", company_slug, resp.status_code)
        return []

    jobs = []
    for item in resp.json().get("jobs", []):
        location = (item.get("location") or {}).get("name", "")
        jobs.append({
            "external_id": f"gh-{item['id']}",
            "title": item.get("title", ""),
            "company": company_slug,
            "location": location,
            "description": _strip_html(item.get("content", "")),
            "tech_stack": "",
            "date_posted": (item.get("updated_at") or "")[:10],
            "apply_url": item.get("absolute_url", ""),
        })

    logger.info("Greenhouse %s: fetched %d job(s)", company_slug, len(jobs))
    return jobs


def fetch_raw_jobs(endpoint: str = "") -> List[dict]:
    """Fetch jobs from all configured Greenhouse company boards."""
    all_jobs: List[dict] = []
    for slug in _GREENHOUSE_SLUGS:
        all_jobs.extend(_fetch_greenhouse(slug))
    logger.info("Total fetched: %d job(s) across %d companies", len(all_jobs), len(_GREENHOUSE_SLUGS))
    return all_jobs


def ingest_all(endpoint: str = "") -> int:
    """Fetch and persist all jobs. Returns count ingested."""
    jobs = fetch_raw_jobs(endpoint)
    upsert_jobs(jobs)
    return len(jobs)
