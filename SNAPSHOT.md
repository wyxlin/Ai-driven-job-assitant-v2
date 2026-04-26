# Snapshot

_Updated after Wave 5 (Production Hardening) — 2026-04-25._

## Implemented Features

### Data Layer (`core/models.py`)
- `LLMStatus` enum: `pending` / `processed` / `failed`
- `Resume`, `Job`, `JobEvaluation` ORM tables (SQLAlchemy 2.x, SQLite + PostgreSQL)
- Public API: `init_db()`, `set_engine()`, `get_session()`, `upsert_jobs()`, `get_pending_jobs()`

### Config (`config.py`)
- `ENV_FILE` env var selects `.env` (prod) or `.env.test` (tests)
- `DB_URL`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MAX_JOBS_PER_RUN=10`

### Services
- `engine.py` — `FilterEngine`:
  - `is_location_match()`: Seattle-area keywords + US-only remote (bare "Remote" passes; "Remote - India" fails via `_has_us_remote` US states allowlist)
  - `is_role_match()`: requires allowlist term (engineer/developer/swe); blocked by staff/principal/lead/director/manager/head/architect/scientist/vp; Senior intentionally allowed
  - `run_filter_pass()`: sets `is_filtered = location_ok AND role_ok` for all NULL rows
- `router.py` — `LLMRouter.evaluate()`: gemini-2.5-flash → GPT-4o-mini → Claude 3 Haiku failover; 429 retries once after 2s; 500 switches immediately
- `fetcher.py` — real Greenhouse API for 5 companies (databricks, anthropic, scaleai, stripe, smartsheet); `_HTMLStripper` cleans job description HTML; fetches ~2100 jobs
- `vetting.py` — `VettingService.process_batch(batch_size)`: loads resume from DB, enforces `MAX_JOBS_PER_RUN` cap, persists `JobEvaluation`, 5s sleep between calls

### CLI (`app.py`)
- `python app.py fetch [--endpoint URL]` — ingest jobs from Greenhouse
- `python app.py filter` — run location + role filter pass
- `python app.py export-filtered [--out PATH]` — export passing jobs to CSV (default: `data/filtered_jobs.csv`)
- `python app.py vet [--batch-size N]` — run automated LLM vetting (secondary path)
- `python app.py report [--min-score N] [--out PATH]` — export LLM-scored results
- `python app.py seed-resume [--file PATH]` — load resume JSON into DB
- `--db URL` global flag overrides database URL

### Prompt Template (`eval_prompt.md`)
- Step 1: context block (resume + skills, paste once per AI conversation)
- Step 2: per-batch scoring instruction (10–15 CSV rows → scored CSV output)
- Step 3: final sort/filter (collect all batches → ranked top list)

### Tests (41 passing)
- `conftest.py` — in-memory SQLite, session-scoped, per-test table reset
- `test_models.py` — Suite A: upsert, idempotency, get_pending_jobs
- `test_filters.py` — Suite B: location match (10), role match (14), run_filter_pass integration (3)
- `test_router.py` — Suite C: TS-C01/C02/C03/C04 + `_is_rate_limited` unit tests (9)

## Pipeline State (2026-04-25)
- `job_assistant.db`: 2100 jobs ingested; 79 with `is_filtered=True`
- `data/filtered_jobs.csv`: 79 jobs ready for manual AI scoring

## Open Bugs
None

## Next Action
Phase 2: use `eval_prompt.md` to batch-score `data/filtered_jobs.csv` via Claude.ai or Codex.
