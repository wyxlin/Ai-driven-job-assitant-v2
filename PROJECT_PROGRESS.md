# Project Progress

## Current Module
Wave 3 — Vetting Service + Fetcher

## Status
Wave 2 COMPLETE (pushed: 5a2ac92). Codex PASS. Wave 3 not started.

## Completed Work
- [x] Directory structure (`core/`, `services/`, `tests/`)
- [x] `requirements.txt`
- [x] `config.py` (with ENV_FILE override for test isolation)
- [x] `.env.test` (placeholder keys only)
- [x] `.gitignore` (protects `.env`, `data/`)
- [x] `core/models.py` — SQLAlchemy 2.x schema: `Resume`, `Job`, `JobEvaluation`, `LLMStatus` enum
- [x] Public interfaces: `init_db()`, `upsert_jobs()`, `get_pending_jobs()`, `get_session()`
- [x] Codex Round 1 review received (3 findings)
- [x] All 3 findings fixed and committed locally (commit: 370775b)
- [x] Wave 1 pushed after Codex PASS
- [x] `services/engine.py` — FilterEngine: `is_location_match()` + `run_filter_pass()`
- [x] `services/router.py` — LLMRouter: Gemini→GPT-4o-mini→Claude Haiku failover with retry

## Known Issues
None open.

## Context Status
Active — Wave 3 window

## Next Step
Implement Wave 3: services/vetting.py + services/fetcher.py
