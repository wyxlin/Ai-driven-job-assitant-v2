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

    def test_remote_us_state_qualifiers(self, engine):
        """US-qualified remote positions are in-scope."""
        assert engine.is_location_match("Remote - California") is True
        assert engine.is_location_match("Remote - New York") is True
        assert engine.is_location_match("Remote - Washington") is True

    def test_remote_non_us_excluded(self, engine):
        """Non-US remote positions must be filtered out."""
        assert engine.is_location_match("Remote - India") is False
        assert engine.is_location_match("Remote - Italy") is False
        assert engine.is_location_match("Remote - Denmark") is False

    def test_remote_non_us_in_multi_location(self, engine):
        """Multi-location string with only non-US remote → False."""
        assert engine.is_location_match("Finland; Remote - Denmark; Stockholm, Sweden") is False

    def test_seattle_in_multi_location_wins(self, engine):
        """Multi-location string containing Seattle → True regardless of other segments."""
        assert engine.is_location_match(
            "Austin, Texas; Seattle, Washington; Remote - Denmark"
        ) is True


class TestIsRoleMatch:
    def test_engineer_title_passes(self, engine):
        assert engine.is_role_match("Software Engineer") is True

    def test_senior_engineer_passes(self, engine):
        """Senior is NOT in blocklist per user spec."""
        assert engine.is_role_match("Senior Software Engineer") is True

    def test_swe_passes(self, engine):
        assert engine.is_role_match("SWE II") is True

    def test_developer_passes(self, engine):
        assert engine.is_role_match("Backend Developer") is True

    def test_ml_engineer_passes(self, engine):
        assert engine.is_role_match("ML Engineer") is True

    def test_scientist_blocked(self, engine):
        assert engine.is_role_match("Data Scientist") is False

    def test_architect_blocked(self, engine):
        assert engine.is_role_match("Solutions Architect") is False

    def test_staff_engineer_blocked(self, engine):
        assert engine.is_role_match("Staff Engineer") is False

    def test_principal_engineer_blocked(self, engine):
        assert engine.is_role_match("Principal Engineer") is False

    def test_engineering_manager_blocked(self, engine):
        assert engine.is_role_match("Engineering Manager") is False

    def test_director_blocked(self, engine):
        assert engine.is_role_match("Director of Engineering") is False

    def test_vp_blocked(self, engine):
        assert engine.is_role_match("VP Engineering") is False

    def test_unrelated_title_fails(self, engine):
        assert engine.is_role_match("Product Manager") is False

    def test_empty_title_fails(self, engine):
        assert engine.is_role_match("") is False


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
