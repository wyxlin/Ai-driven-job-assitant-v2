# Snapshot

_Generated after Wave 1 — overwrite at end of each module._

## Implemented Features
- Project scaffold: `core/`, `services/`, `tests/`, `requirements.txt`, `config.py`, `.env.test`
- Data layer (`core/models.py`):
  - `LLMStatus` enum: `pending` / `processed` / `failed`
  - `Resume` table: `id`, `structured_data` (JSON/JSONB via `with_variant`), `created_at`
  - `Job` table: `id`, `external_id` (unique), `title`, `company`, `location`, `description`, `tech_stack`, `date_posted`, `apply_url`, `is_filtered`, `llm_status`, `created_at`
  - `JobEvaluation` table: `id`, `job_id` (FK→Job), `match_score`, `reasoning`, `model_used`, `created_at`
  - Public API: `init_db(engine)`, `set_engine()`, `get_session()`, `upsert_jobs(data)`, `get_pending_jobs(limit)`
- Config loader: `ENV_FILE` env var selects `.env` (prod) or `.env.test` (tests)
- Workflow tracking: `MODULE_PLAN.md`, `PROJECT_PROGRESS.md`, `SNAPSHOT.md`

## Open Bugs
None

## Current State
Wave 1 complete and pushed (commit: 11a5813). Codex verdict: PASS.

## Current Module
Wave 2 — Filter Engine + LLM Router

## Next Action
Implement `services/engine.py` (FilterEngine) + `services/router.py` (LLMRouter) in parallel
