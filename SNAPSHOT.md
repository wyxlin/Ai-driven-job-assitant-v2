# Snapshot

_Generated after Wave 2 — overwrite at end of each module._

## Implemented Features
- Project scaffold: `core/`, `services/`, `tests/`, `requirements.txt`, `config.py`, `.env.test`
- Data layer (`core/models.py`):
  - `LLMStatus` enum: `pending` / `processed` / `failed`
  - `Resume` table: `id`, `structured_data` (JSON/JSONB via `with_variant`), `created_at`
  - `Job` table: `id`, `external_id` (unique), `title`, `company`, `location`, `description`, `tech_stack`, `date_posted`, `apply_url`, `is_filtered`, `llm_status`, `created_at`
  - `JobEvaluation` table: `id`, `job_id` (FK→Job), `match_score`, `reasoning`, `model_used`, `created_at`
  - Public API: `init_db(engine)`, `set_engine()`, `get_session()`, `upsert_jobs(data)`, `get_pending_jobs(limit)`
- Config loader: `ENV_FILE` env var selects `.env` (prod) or `.env.test` (tests)
- Filter engine (`services/engine.py`):
  - `FilterEngine.is_location_match(location_str)` — case-insensitive keyword match against 8 Seattle-area + Remote keywords
  - `FilterEngine.run_filter_pass()` — queries `is_filtered IS NULL` jobs, writes True/False
- LLM router (`services/router.py`):
  - `LLMRouter.evaluate(resume, job_desc)` → `{"match_score": int, "reasoning": str, "model_used": str}` or `None`
  - Failover: Gemini 1.5 Flash → GPT-4o-mini → Claude 3 Haiku
  - Retry: 429 or 500 → sleep 2s, one retry; second failure → next provider
  - All fail → `logger.critical`, return `None`
- Workflow tracking: `MODULE_PLAN.md`, `PROJECT_PROGRESS.md`, `SNAPSHOT.md`

## Open Bugs
None

## Current State
Wave 2 pushed (5a2ac92). Codex PASS.

## Current Module
Wave 3 — Vetting Service + Fetcher

## Next Action
Implement `services/vetting.py` + `services/fetcher.py`
