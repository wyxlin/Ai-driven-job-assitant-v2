# Project Progress

## Current Phase
—— Phase 1 complete. Awaiting Phase 2 (manual AI scoring) results. ——

## Status
Wave 5 (Production Hardening) COMPLETE. 41 tests passing. Pipeline producing `data/filtered_jobs.csv`.

## Completed Work
- [x] Directory structure (`core/`, `services/`, `tests/`)
- [x] `requirements.txt` (includes pytest-mock)
- [x] `config.py` (with ENV_FILE override for test isolation)
- [x] `.env.test` (placeholder keys only)
- [x] `.gitignore` (protects `.env`, `data/`)
- [x] `core/models.py` — SQLAlchemy 2.x schema: `Resume`, `Job`, `JobEvaluation`, `LLMStatus` enum
- [x] Public interfaces: `init_db()`, `upsert_jobs()`, `get_pending_jobs()`, `get_session()`
- [x] `services/engine.py` — FilterEngine: location filter (Seattle-area + US-only remote via `_has_us_remote`) + role filter (`is_role_match` with allowlist/blocklist); `run_filter_pass()` requires both
- [x] `services/router.py` — LLMRouter: gemini-2.5-flash → GPT-4o-mini → Claude 3 Haiku failover; 429 retries once after 2s; 500 switches immediately
- [x] `services/fetcher.py` — real Greenhouse API for 5 companies (databricks, anthropic, scaleai, stripe, smartsheet); HTML stripping via `_HTMLStripper`
- [x] `services/vetting.py` — `VettingService.process_batch(batch_size)`, DB resume load, MAX_JOBS_PER_RUN cap
- [x] `app.py` — CLI: `fetch` / `filter` / `vet` / `export-filtered` / `seed-resume` / `report` subcommands
- [x] `eval_prompt.md` — three-step prompt template for manual AI batch scoring
- [x] `tests/conftest.py` — in-memory SQLite, session-scoped engine, per-test table reset
- [x] `tests/test_models.py` — Suite A: upsert, idempotency, get_pending_jobs
- [x] `tests/test_filters.py` — Suite B: location match, role match (41 cases), run_filter_pass integration
- [x] `tests/test_router.py` — Suite C: TS-C01/C02/C03/C04, _is_rate_limited unit tests

## Production Run Results (2026-04-25)
- Fetched: 2100 jobs across 5 Greenhouse companies
- After location filter only (old): 404 passed
- After location + role filter (current): **79 passed** → exported to `data/filtered_jobs.csv`

## Known Issues
None.

## Next Step
Phase 2: batch `data/filtered_jobs.csv` into Claude.ai / Codex using `eval_prompt.md`, collect scored results.
Phase 3: TBD based on scored output (apply tracking, cover letter tailoring, etc.)
