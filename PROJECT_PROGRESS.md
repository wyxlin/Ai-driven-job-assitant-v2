# Project Progress

## Current Module
Wave 4 — Entry Point + Tests

## Status
Wave 3 COMPLETE (pushed: 497e001). Codex PASS. Wave 4 not started.

## Completed Work
- [x] Directory structure (`core/`, `services/`, `tests/`)
- [x] `requirements.txt`
- [x] `config.py` (with ENV_FILE override for test isolation)
- [x] `.env.test` (placeholder keys only)
- [x] `.gitignore` (protects `.env`, `data/`)
- [x] `core/models.py` — SQLAlchemy 2.x schema: `Resume`, `Job`, `JobEvaluation`, `LLMStatus` enum
- [x] Public interfaces: `init_db()`, `upsert_jobs()`, `get_pending_jobs()`, `get_session()`
- [x] `services/engine.py` — FilterEngine: `is_location_match()` + `run_filter_pass()`
- [x] `services/router.py` — LLMRouter: Gemini→GPT-4o-mini→Claude Haiku failover with retry
- [x] `services/fetcher.py` — `fetch_raw_jobs(endpoint)` stub + `ingest_all(endpoint)`
- [x] `services/vetting.py` — `VettingService.process_batch(batch_size)`, DB resume load, MAX_JOBS_PER_RUN cap

## Known Issues
None open.

## Context Status
Active — Wave 4 window

## Next Step
Implement Wave 4: app.py (CLI) + full TSD test suite (tests/)
