# Project Progress

## Current Module
—— All waves complete ——

## Status
Wave 4 COMPLETE (pushed: 29bb900). Codex PASS. Project at v1.0.

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
- [x] `app.py` — CLI: `fetch` / `filter` / `vet` subcommands
- [x] `tests/conftest.py` — in-memory SQLite, session-scoped engine, per-test table reset
- [x] `tests/test_models.py` — Suite A: upsert, idempotency, get_pending_jobs
- [x] `tests/test_filters.py` — Suite B: TS-B01/B02/B03, run_filter_pass integration
- [x] `tests/test_router.py` — Suite C: TS-C01/C02/C03/C04, _is_rate_limited unit tests

## Known Issues
None. Residual note from Codex: session-scoped SQLite engine is fine for serial tests;
revisit if parallel test execution is added later.

## Next Step
Production readiness: seed real resume, configure .env with live API keys, run end-to-end.
