"""TSD Suite B — FilterEngine.is_location_match + run_filter_pass."""
import pytest

from core.models import Job, get_session, upsert_jobs
from services.engine import FilterEngine


@pytest.fixture
def engine():
    return FilterEngine()


class TestIsLocationMatch:
    def test_b01_seattle_area_and_remote(self, engine):
        """TS-B01: Remote, Kirkland WA, SEATTLE → True."""
        assert engine.is_location_match("Remote") is True
        assert engine.is_location_match("Kirkland, WA") is True
        assert engine.is_location_match("SEATTLE") is True

    def test_b02_out_of_area(self, engine):
        """TS-B02: Austin TX, London UK → False."""
        assert engine.is_location_match("Austin, TX") is False
        assert engine.is_location_match("London, UK") is False

    def test_b03_lowercase_keyword(self, engine):
        """TS-B03: 'redmond' (lowercase) → True."""
        assert engine.is_location_match("redmond") is True

    def test_bellevue(self, engine):
        assert engine.is_location_match("Bellevue, WA") is True

    def test_greater_seattle_area(self, engine):
        assert engine.is_location_match("Greater Seattle Area") is True

    def test_empty_string(self, engine):
        assert engine.is_location_match("") is False


class TestRunFilterPass:
    def _seed_jobs(self, jobs):
        upsert_jobs(jobs)

    def test_sets_is_filtered_true_for_seattle_jobs(self):
        self._seed_jobs([
            {"external_id": "f-sea", "title": "SWE", "company": "A",
             "location": "Seattle, WA", "description": "", "tech_stack": "",
             "date_posted": "2026-04-01", "apply_url": ""},
            {"external_id": "f-rem", "title": "SWE", "company": "B",
             "location": "Remote", "description": "", "tech_stack": "",
             "date_posted": "2026-04-01", "apply_url": ""},
        ])
        FilterEngine().run_filter_pass()
        with get_session() as session:
            jobs = {j.external_id: j.is_filtered for j in session.query(Job).all()}
        assert jobs["f-sea"] is True
        assert jobs["f-rem"] is True

    def test_sets_is_filtered_false_for_out_of_area(self):
        self._seed_jobs([
            {"external_id": "f-atx", "title": "SWE", "company": "C",
             "location": "Austin, TX", "description": "", "tech_stack": "",
             "date_posted": "2026-04-01", "apply_url": ""},
        ])
        FilterEngine().run_filter_pass()
        with get_session() as session:
            job = session.query(Job).filter_by(external_id="f-atx").one()
            assert job.is_filtered is False

    def test_skips_already_filtered_jobs(self):
        """run_filter_pass() only processes is_filtered IS NULL rows."""
        with get_session() as session:
            session.add(Job(
                external_id="f-skip",
                title="SWE", company="D",
                location="Austin, TX",
                is_filtered=True,  # already set
            ))
        FilterEngine().run_filter_pass()
        with get_session() as session:
            job = session.query(Job).filter_by(external_id="f-skip").one()
            assert job.is_filtered is True  # unchanged
