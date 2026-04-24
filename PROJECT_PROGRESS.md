# Project Progress

## Current Module
Wave 2 — Filter Engine + LLM Router

## Status
Wave 1 COMPLETE (Codex PASS, pushed). Wave 2 not started.

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

## Known Issues
None open. Three Codex findings resolved:
- [FIXED] `_structured_data_column()` now uses `JSON().with_variant(JSONB(), "postgresql")` — dialect-safe
- [FIXED] SQLite upsert now uses `on_conflict_do_nothing(index_elements=["external_id"])` — scope-correct
- [FIXED] `config.py` now supports `ENV_FILE` env var for test isolation

## Context Status
Active — Wave 1 window

## Next Step
Begin Wave 2: implement `services/engine.py` + `services/router.py` in parallel
