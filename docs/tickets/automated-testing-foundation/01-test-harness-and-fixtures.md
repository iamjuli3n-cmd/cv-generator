---
ticket: 01
title: Test harness + fixtures
status: ready-for-agent
spec: docs/specs/automated-testing-foundation.md
adr: docs/adr/0001-sqlite-for-test-database.md
---

# 01: Test harness + fixtures

## Goal

Give the project a working, reusable pytest test harness, so that any future test suite — starting with Tickets 02 and 03 — can write tests against an isolated database and an authenticated HTTP client without building any of that infrastructure itself.

## Scope

- Refactor `database.py`'s eager module-level `engine = create_engine(DATABASE_URL)` / `SessionLocal = sessionmaker(...)` into lazy singletons — e.g. `get_engine()` and `get_sessionmaker()` functions that build the engine/sessionmaker on first call, reading `DATABASE_URL` at that point rather than at import time. `get_db()` should call `get_sessionmaker()` instead of referencing a module-level `SessionLocal`. Keep the same environment-variable-driven configuration style; do not introduce an application factory or a settings object.
- Add `requirements-dev.txt` with `pytest`, `pytest-cov`, and `httpx` (required by Starlette's `TestClient`).
- Create a `tests/` directory and add pytest configuration (`pyproject.toml`'s `[tool.pytest.ini_options]`, or `pytest.ini`) setting `testpaths = ["tests"]`.
- Add `tests/conftest.py` with:
  - A session-scoped fixture that creates one file-based SQLite database (via pytest's `tmp_path_factory`), enables `PRAGMA foreign_keys=ON` on connections to it, and runs `Base.metadata.create_all` against it once.
  - A function-scoped `db_session` fixture: opens a connection, begins an outer transaction, starts a SAVEPOINT-backed nested transaction bound to a `Session`, yields that `Session`, then rolls back the transaction and closes the connection after the test.
  - A function-scoped `client` fixture: builds a `TestClient(app)` with `app.dependency_overrides[get_db]` set to yield the `db_session` fixture's session, and clears the override during teardown.
  - A generic, domain-agnostic fixture/helper that creates a user directly in the database and returns it — e.g. `create_user(db_session, email, password) -> models.User` — hashing the password with `auth.hash_password`, no HTTP call involved.
  - A generic, domain-agnostic fixture/helper that mints a valid bearer-auth header for a given user without an HTTP call — e.g. `auth_headers(user) -> dict[str, str]`, built via `auth.create_access_token`.
- Add one smoke test (e.g. `tests/test_harness_smoke.py`) that uses the `client` fixture to hit a safe, unauthenticated endpoint (e.g. `GET /openapi.json`) and asserts a 200, proving the harness itself works end to end.

## Acceptance Criteria

- [ ] `pip install -r requirements.txt -r requirements-dev.txt && pytest` succeeds with no manual setup: no `.env` file, no real PostgreSQL instance, no manually created database.
- [ ] Importing `database` (directly, or transitively via `main`) does not raise when `DATABASE_URL` is unset.
- [ ] The `db_session` fixture is isolated per test: data written in one test is not visible in another test.
- [ ] The `client` fixture's requests are served against `db_session`'s isolated database, never a real one.
- [ ] The user-creation and token-minting helpers produce a `User` row and a token that successfully authenticates against `get_current_user`, with no HTTP call involved in their own operation.
- [ ] The smoke test exists, passes, and has no dependency on Tickets 02 or 03.
- [ ] Running `pytest` does not attempt to collect `cv_test.py` (the sample-CV fixture-data module at the repo root) as a test module.
- [ ] `requirements-dev.txt`'s contents are not required by `requirements.txt` or by any production code path.

## Relevant Context/Files

- `database.py` — currently: `DATABASE_URL = os.getenv("DATABASE_URL")`, `engine = create_engine(DATABASE_URL)`, `SessionLocal = sessionmaker(bind=engine, ...)` at module level; `get_db()` yields `SessionLocal()`. This file is what becomes lazy.
- `main.py` — `from database import get_db`; `app = FastAPI(title="CV Generator")` is the object the `client` fixture wraps. Note the module-level `from cv_test import cv_test` — this is a harmless import of static sample data, not a live dependency, and does not need to change.
- `models.py` — exposes `Base` (imported from `database.py`) and the `User` model (`id_user`, `email`, `hashed_password`, `is_active`, `date_creation`), used by the user-creation helper.
- `auth.py` — `hash_password`, `create_access_token`, `get_current_user`. `SECRET_KEY` reads from an env var with a fallback default (`"changeme-in-production"`), so no environment configuration is required for tokens created and verified within the same test process.
- `cv_test.py` (repo root) — sample CV fixture data, not a test file, despite its name matching pytest's default `*_test.py` discovery pattern. The `testpaths` config in this ticket must prevent it from being collected.
- `requirements.txt` — current runtime dependencies; test tooling does not belong here.
- `docs/adr/0001-sqlite-for-test-database.md` — why SQLite (not Postgres) backs this harness.
- `docs/specs/automated-testing-foundation.md` — full rationale and decisions for this initiative.

## Blocked By

None (can start immediately).

## Why That Blocking Edge Is Real

N/A — nothing in the codebase or this initiative needs to exist before this ticket starts.

## What Would Break If Attempted In The Opposite Order

N/A — this is the first ticket in the sequence; nothing precedes it.
