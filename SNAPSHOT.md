# Snapshot

_Generated after Wave 4 (project complete) — overwrite if further development begins._

## Implemented Features

### Data Layer (`core/models.py`)
- `LLMStatus` enum: `pending` / `processed` / `failed`
- `Resume`, `Job`, `JobEvaluation` ORM tables (SQLAlchemy 2.x, SQLite + PostgreSQL)
- Public API: `init_db()`, `set_engine()`, `get_session()`, `upsert_jobs()`, `get_pending_jobs()`

### Config (`config.py`)
- `ENV_FILE` env var selects `.env` (prod) or `.env.test` (tests)
- `DB_URL`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MAX_JOBS_PER_RUN=200`

### Services
- `engine.py` — `FilterEngine.is_location_match()` + `run_filter_pass()` (8 Seattle-area keywords)
- `router.py` — `LLMRouter.evaluate()`: Gemini 1.5 Flash → GPT-4o-mini → Claude 3 Haiku failover; 429 retries once after 2s; 500 switches immediately
- `fetcher.py` — `fetch_raw_jobs(endpoint)` stub + `ingest_all(endpoint)` (6 fixture jobs)
- `vetting.py` — `VettingService.process_batch(batch_size)`: loads resume from DB, enforces `MAX_JOBS_PER_RUN` cap, persists `JobEvaluation` + updates `llm_status`

### CLI (`app.py`)
- `python app.py fetch [--endpoint URL]` — ingest jobs
- `python app.py filter` — run location filter pass
- `python app.py vet [--batch-size N]` — run LLM vetting
- `--db URL` global flag overrides database URL

### Tests (23 passing)
- `conftest.py` — in-memory SQLite, session-scoped, per-test table reset
- `test_models.py` — Suite A (upsert, idempotency, get_pending_jobs)
- `test_filters.py` — Suite B: TS-B01/B02/B03 + run_filter_pass integration
- `test_router.py` — Suite C: TS-C01/C02/C03/C04 + `_is_rate_limited` unit tests

## Open Bugs
None

## Current State
All 4 waves complete and pushed. Codex PASS on every wave.

## Next Action
Production run: populate `data/resume.json` → seed `Resume` table → configure `.env` with live keys → `python app.py fetch && python app.py filter && python app.py vet`
