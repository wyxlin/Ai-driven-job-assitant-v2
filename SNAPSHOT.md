# Snapshot

_Generated after Wave 1. Overwrite this file at the end of each module._

## Implemented Features
- Project scaffold: `core/`, `services/`, `tests/`, `requirements.txt`, `config.py`, `.env.test`
- Data layer (`core/models.py`):
  - `LLMStatus` enum: `pending` / `processed` / `failed`
  - `Resume` table: `id`, `structured_data` (JSON/JSONB), `created_at`
  - `Job` table: `id`, `external_id` (unique), `title`, `company`, `location`, `description`, `tech_stack`, `date_posted`, `apply_url`, `is_filtered`, `llm_status`, `created_at`
  - `JobEvaluation` table: `id`, `job_id` (FK), `match_score`, `reasoning`, `model_used`, `created_at`
  - Public API: `init_db()`, `set_engine()`, `get_session()`, `upsert_jobs()`, `get_pending_jobs()`
- Config loader (`config.py`): reads `DATABASE_URL`, `*_API_KEY`, `MAX_JOBS_PER_RUN` from env file specified by `ENV_FILE`

## Open Bugs
None

## Current State
Wave 1 complete. Two local commits not yet pushed (pending Codex re-confirmation):
- `feat: Wave 1 — scaffold + data layer (models.py)`
- `fix: address Codex Wave 1 review — dialect-safe JSON, sqlite upsert, env isolation`

## Current Module
Wave 1 — Scaffold + Data Layer

## Next Action
Codex Round 2 re-review → PASS → push → begin Wave 2 (engine.py + router.py)
