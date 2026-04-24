# Snapshot

_Generated after Wave 3 — overwrite at end of each module._

## Implemented Features
- Project scaffold: `core/`, `services/`, `tests/`, `requirements.txt`, `config.py`, `.env.test`
- Data layer (`core/models.py`):
  - `LLMStatus` enum: `pending` / `processed` / `failed`
  - `Resume` table: `id`, `structured_data` (JSON/JSONB), `created_at`
  - `Job` table: `id`, `external_id`, `title`, `company`, `location`, `description`, `tech_stack`, `date_posted`, `apply_url`, `is_filtered`, `llm_status`, `created_at`
  - `JobEvaluation` table: `id`, `job_id` (FK), `match_score`, `reasoning`, `model_used`, `created_at`
  - Public API: `init_db()`, `set_engine()`, `get_session()`, `upsert_jobs()`, `get_pending_jobs()`
- Config loader (`config.py`): `ENV_FILE` override, `MAX_JOBS_PER_RUN=200`
- Filter engine (`services/engine.py`):
  - `FilterEngine.is_location_match(location_str)` — 8 keywords, case-insensitive
  - `FilterEngine.run_filter_pass()` — writes `is_filtered` for all NULL rows
- LLM router (`services/router.py`):
  - `LLMRouter.evaluate(resume, job_desc)` → `{"match_score", "reasoning", "model_used"}` or `None`
  - Failover: Gemini 1.5 Flash → GPT-4o-mini → Claude 3 Haiku
  - 429 retries once after 2s; 500 switches immediately
- Job fetcher (`services/fetcher.py`):
  - `fetch_raw_jobs(endpoint)` — stub, returns 6 fixture jobs
  - `ingest_all(endpoint)` — fetch + upsert, returns count
- Vetting service (`services/vetting.py`):
  - `VettingService.process_batch(batch_size)` — loads resume from DB, processes up to `min(batch_size, MAX_JOBS_PER_RUN)` pending jobs
  - Persists `JobEvaluation`, sets `llm_status=processed/failed`

## Open Bugs
None

## Current State
Wave 3 pushed (497e001). Codex PASS.

## Current Module
Wave 4 — Entry Point + Tests

## Next Action
Implement `app.py` (CLI: `fetch`, `filter`, `vet` subcommands) + full TSD test suite in `tests/`
