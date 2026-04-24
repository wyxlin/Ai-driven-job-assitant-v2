# Module Plan

## Execution Order

| Wave | Module | Files | Status |
|------|--------|-------|--------|
| 1 | Scaffold + Data Layer | `config.py`, `requirements.txt`, `.env.test`, `core/models.py` | ✅ Complete |
| 2 | Filter Engine + LLM Router | `services/engine.py`, `services/router.py` | ⏳ Pending |
| 3 | Vetting Service + Fetcher | `services/vetting.py`, `services/fetcher.py` | ⏳ Pending |
| 4 | Entry Point + Tests | `app.py`, `tests/conftest.py`, `tests/test_models.py`, `tests/test_filters.py`, `tests/test_router.py` | ⏳ Pending |

## Module Boundaries

### Wave 1 — Scaffold + Data Layer
- **Scope:** Directory structure, SQLAlchemy ORM schema, config loader, env files
- **Non-Scope:** Any service logic, LLM calls, filtering, CLI

### Wave 2 — Filter Engine + LLM Router
- **Scope:** Geographic keyword filter (`engine.py`), multi-LLM failover gateway (`router.py`)
- **Non-Scope:** Batch orchestration, job fetching, tests, CLI

### Wave 3 — Vetting Service + Fetcher
- **Scope:** Batch processing loop (`vetting.py`), Greenhouse/Lever stub with fixture data (`fetcher.py`)
- **Non-Scope:** Tests, CLI, LLM prompt content

### Wave 4 — Entry Point + Tests
- **Scope:** CLI app (`app.py`), full TSD test suite
- **Non-Scope:** New features, schema changes

## Parallelization
- Within each wave: both modules run in parallel (no inter-dependency)
- Across waves: sequential (each wave depends on the previous)

## Dependent Docs
- PRD: phase 1 scope, location filter rules, LLM router spec
- TDD: module interfaces, directory structure, failover logic, safety brake
- TSD: test cases TS-A01 through TS-D02, integration scenario
- SPS: resume JSONB schema, LLM prompt templates, evaluation output schema
