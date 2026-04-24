"""TSD Suite A — data layer (upsert_jobs, get_pending_jobs)."""
import pytest

from core.models import LLMStatus, get_pending_jobs, get_session, upsert_jobs, Job


_SAMPLE_JOBS = [
    {
        "external_id": "test-001",
        "title": "Backend Engineer",
        "company": "Acme",
        "location": "Seattle, WA",
        "description": "Build scalable services.",
        "tech_stack": "Python,PostgreSQL",
        "date_posted": "2026-04-01",
        "apply_url": "https://acme.example.com/jobs/1",
    },
    {
        "external_id": "test-002",
        "title": "ML Engineer",
        "company": "Horizon",
        "location": "Remote",
        "description": "Train and deploy models.",
        "tech_stack": "Python,PyTorch",
        "date_posted": "2026-04-02",
        "apply_url": "https://horizon.example.com/jobs/2",
    },
]


class TestUpsertJobs:
    def test_inserts_records(self):
        """TS-A01: upsert_jobs() inserts all provided records."""
        upsert_jobs(_SAMPLE_JOBS)
        with get_session() as session:
            count = session.query(Job).count()
        assert count == 2

    def test_idempotent_on_duplicate_external_id(self):
        """TS-A02: duplicate external_id is silently ignored (no duplicate row)."""
        upsert_jobs(_SAMPLE_JOBS)
        upsert_jobs(_SAMPLE_JOBS)  # second call must not raise or double-insert
        with get_session() as session:
            count = session.query(Job).count()
        assert count == 2

    def test_empty_list_is_noop(self):
        upsert_jobs([])
        with get_session() as session:
            count = session.query(Job).count()
        assert count == 0


class TestGetPendingJobs:
    def _seed_with_filter(self, external_id, is_filtered, llm_status=LLMStatus.pending):
        with get_session() as session:
            session.add(
                Job(
                    external_id=external_id,
                    title="Test",
                    company="Co",
                    location="Seattle, WA",
                    is_filtered=is_filtered,
                    llm_status=llm_status,
                )
            )

    def test_returns_filtered_pending_jobs(self):
        """Only is_filtered=True + llm_status=pending jobs are returned."""
        self._seed_with_filter("p-in", is_filtered=True, llm_status=LLMStatus.pending)
        self._seed_with_filter("p-out", is_filtered=False, llm_status=LLMStatus.pending)
        self._seed_with_filter("p-null", is_filtered=None, llm_status=LLMStatus.pending)
        self._seed_with_filter("p-done", is_filtered=True, llm_status=LLMStatus.processed)

        jobs = get_pending_jobs()
        assert len(jobs) == 1
        assert jobs[0].external_id == "p-in"

    def test_respects_limit(self):
        for i in range(5):
            self._seed_with_filter(f"lim-{i}", is_filtered=True)
        jobs = get_pending_jobs(limit=3)
        assert len(jobs) == 3
