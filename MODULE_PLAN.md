# Module Plan

## Execution Order

| Wave | Module | Files | Status |
|------|--------|-------|--------|
| 1 | Scaffold + Data Layer | `config.py`, `requirements.txt`, `.env.test`, `core/models.py` | ✅ Complete |
| 2 | Filter Engine + LLM Router | `services/engine.py`, `services/router.py` | ✅ Complete |
| 3 | Vetting Service + Fetcher | `services/vetting.py`, `services/fetcher.py` | ✅ Complete |
| 4 | Entry Point + Tests | `app.py`, `tests/conftest.py`, `tests/test_models.py`, `tests/test_filters.py`, `tests/test_router.py` | ✅ Complete |
| 5 | Production Hardening | `services/engine.py`, `services/fetcher.py`, `app.py` | ✅ Complete |

## Module Boundaries

### Wave 1 — Scaffold + Data Layer
- **Scope:** Directory structure, SQLAlchemy ORM schema, config loader, env files
- **Non-Scope:** Any service logic, LLM calls, filtering, CLI

### Wave 2 — Filter Engine + LLM Router
- **Scope:** Geographic keyword filter (`engine.py`), multi-LLM failover gateway (`router.py`)
- **Non-Scope:** Batch orchestration, job fetching, tests, CLI

### Wave 3 — Vetting Service + Fetcher
- **Scope:** Batch processing loop (`vetting.py`), Greenhouse API integration (`fetcher.py`)
- **Non-Scope:** Tests, CLI, LLM prompt content

### Wave 4 — Entry Point + Tests
- **Scope:** CLI app (`app.py`), full TSD test suite
- **Non-Scope:** New features, schema changes

### Wave 5 — Production Hardening
- **Scope:**
  - `engine.py`: US-only remote filter (`_has_us_remote`), role/title filter (`is_role_match`)
  - `fetcher.py`: real Greenhouse API for 5 companies, HTML stripping
  - `app.py`: `export-filtered` and `seed-resume` subcommands
  - `eval_prompt.md`: manual AI batch scoring template
- **Non-Scope:** Schema changes, new LLM providers

## Pipeline Architecture

### Phase 1 — Automated (current primary flow)
```
fetch → filter → export-filtered → data/filtered_jobs.csv
```
- `fetch`: pulls ~2100 jobs from Greenhouse (databricks, anthropic, scaleai, stripe, smartsheet)
- `filter`: applies location filter (Seattle-area + US-only remote) AND role filter (allowlist/blocklist)
- `export-filtered`: dumps 79 passing jobs to CSV with full descriptions

### Phase 2 — Semi-manual AI scoring
```
data/filtered_jobs.csv → AI chat (Claude.ai / Codex) → scored CSV
```
- User batches 10–15 rows at a time using `eval_prompt.md` template
- No API keys or rate limits required
- Output: ranked CSV with score, pros, cons per job

### Phase 3 — TBD
- Use ranked results for next actions (apply tracking, tailored cover letters, etc.)

## Parallelization
- Within each wave: modules run in parallel where no inter-dependency exists
- Across waves: sequential (each wave depends on the previous)

## Dependent Docs
- PRD: phase 1 scope, location filter rules, LLM router spec
- TDD: module interfaces, directory structure, failover logic, safety brake
- TSD: test cases TS-A01 through TS-D02, integration scenario
- SPS: resume JSONB schema, LLM prompt templates, evaluation output schema
