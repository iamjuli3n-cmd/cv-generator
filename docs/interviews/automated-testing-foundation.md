# Interview: Automated testing foundation + CI integration

**Status**: Step 1 (interview) complete. Step 2 (`/to-spec`) and ticket creation (`/to-tickets`) are separate, later steps — not done here.

## Goal

Add a complete automated testing foundation and CI integration to the existing FastAPI CV Generator project, as four units of work:

1. Test harness + fixtures
2. Auth test suite
3. CV CRUD + ownership test suite
4. CI integration

## Dependency graph

```
Unit 1 (harness) ──┬─▶ Unit 2 (auth suite)   ──┐
                    └─▶ Unit 3 (CV/ownership) ──┴─▶ Unit 4 (CI integration)
```

- Units 2 and 3 are blocked by Unit 1 (stated by the requester): both need the reusable `TestClient`, isolated test database, fixtures, and setup/teardown that Unit 1 builds.
- Unit 4 is blocked by **both** Unit 2 and Unit 3 — this was inferred during the interview (not originally stated) and explicitly confirmed by the requester: Unit 4 also updates the README to claim automated tests exist and adds a passing CI badge, which would be misleading if it shipped before real test coverage exists in Units 2/3.

## Facts established about the codebase (Step 0, before questioning)

- No test tooling exists at all: no `pytest`, no `httpx`, no `conftest.py`, no pytest config, no `.github/workflows/`.
- `database.py` builds the SQLAlchemy engine eagerly at import time (`engine = create_engine(DATABASE_URL)`), reading `DATABASE_URL` from `.env` via `python-dotenv`. If unset, this crashes immediately on import — so any isolated test run needs this fixed regardless of which test database backend is chosen.
- `requirements.txt` has no Postgres driver (`psycopg2-binary`/`psycopg`) despite the app requiring PostgreSQL in production and the README documenting it as a dependency. Pre-existing gap, out of scope here (see "Out of scope").
- `cv_test.py` at the repo root matches pytest's default `*_test.py` discovery pattern but contains only fixture data (`cv_test = CV(...)`), not real tests — a naming collision to guard against, not fix by renaming.
- Auth: JWT (`python-jose`), bcrypt via `passlib`, 24h token expiry, `SECRET_KEY` env var (has a fallback default).
- Ownership: CV routes filter by `id_user`; cross-user access deliberately returns **404, not 403** (documented in code comments as intentional, to avoid leaking existence of another user's CV).
- `PUT /cv/{id}` does a full delete-and-recreate of child rows — no partial-update semantics.
- No `CONTEXT.md` exists yet in this repo (domain-modeling docs are created lazily; not needed for this initiative since nothing here changes business/domain vocabulary).
- This development machine has no `python`, `pip`, `docker`, or `gh` on PATH in either shell available to the interviewer — doesn't block CI design (GitHub Actions runs its own environment) but does block filing GitHub issues directly from this session.

## Decisions

### Round 1

| # | Decision | Chosen |
|---|----------|--------|
| Q1 | Test database backend | File-based SQLite (not real Postgres, not testcontainers) — no Postgres-specific types in `models.py`; Docker unavailable locally. Recorded as [ADR-0001](../adr/0001-sqlite-for-test-database.md). |
| Q2 | `database.py`'s eager engine creation | Refactor to lazy/testable rather than working around it purely from test-side env-var tricks. |
| Q3 | Missing Postgres driver gap | Out of scope for this initiative; track separately. |
| Q4 | Test layout / `cv_test.py` collision | Create `tests/` + pytest `testpaths` config; leave `cv_test.py` unchanged. |
| Q5 | Test/dev dependencies | Separate `requirements-dev.txt` (pytest, pytest-cov, httpx), not folded into `requirements.txt`. |
| Q6 | Auth suite scope | Confirmed as listed (see Unit 2 scope below). |
| Q7 | CV/ownership suite scope | Confirmed as listed (see Unit 3 scope below). |
| Q8 | CI trigger/runner/scope | Python 3.10, push + PR to `main`, `ubuntu-latest` only, tests only (no lint/type-check). |

### Round 2

| # | Decision | Chosen |
|---|----------|--------|
| Q1 | Lazy engine refactor shape | Keep the env-var-driven `DATABASE_URL` config style; make `engine`/`SessionLocal` lazy module-level singletons built on first use via `get_engine()`/`get_sessionmaker()`. No application-factory refactor. Consequence: since tests fully override the `get_db` FastAPI dependency, `DATABASE_URL` need not be set at all to run the suite. |
| Q2 | Per-test isolation mechanic | One file-based SQLite database for the whole test session; tables created once; each test wrapped in a SAVEPOINT-based nested transaction, rolled back afterward. |
| Q3 | How Unit 3's fixtures create users | Direct DB insert + `create_access_token()` call (no HTTP round-trip). Unit 2 remains the only suite that exercises the real register/login HTTP flow. |
| Q4 | Coverage gate | `pytest-cov` reports coverage; no enforced minimum threshold yet. |
| Q5 | Branch protection | This CI workflow is **not** made a required status check yet; revisit once the suite has been stable and green for a while. |
| Q6 | Specification delivery format | Four linked GitHub issues (one per unit), `ready-for-agent` label, native issue-dependency links — per this repo's documented issue-tracker convention (`docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`). Deferred to the `/to-tickets` step. |
| Q7 | ADR | Record the SQLite-vs-Postgres test database decision as an ADR. Done: [`docs/adr/0001-sqlite-for-test-database.md`](../adr/0001-sqlite-for-test-database.md). |

### Round 3

| # | Decision | Chosen |
|---|----------|--------|
| Q1 | Fixture ownership boundary | The generic authenticated-user helper (direct-DB user creation + token minting) lives in Unit 1's `tests/conftest.py`, not inside Unit 3 — it's domain-agnostic harness functionality, reusable by any future suite. |
| Q2 | Unit 1 acceptance criterion | Unit 1 includes one trivial smoke test (e.g. hitting `/openapi.json` through the isolated-DB `client` fixture) so the harness has an independent, mergeable "done" signal before Units 2/3 build on it. |
| Q3 | README scope in Unit 4 | Unit 4 also marks "Tests automatisés (pytest)" done in the README Roadmap and adds a CI status badge, so the docs stay truthful about what shipped. |

### Post-round-3 clarification

- Accepted: Unit 4 is blocked by **both** Unit 2 and Unit 3 (see "Dependency graph" above).
- GitHub issue creation explicitly deferred to a later `/to-tickets` step — not done in this session.

## Unit scope summary (for `/to-spec`)

### Unit 1 — Test harness + fixtures
*Blocked by: none.*

- Refactor `database.py`: convert the eager `engine`/`SessionLocal` module-level statements into lazy singletons behind `get_engine()`/`get_sessionmaker()`, built on first call; `get_db()` uses `get_sessionmaker()`. Same env-var-driven config style, no application-factory refactor.
- Add `requirements-dev.txt`: `pytest`, `pytest-cov`, `httpx`.
- Add `tests/` directory; add pytest config (`pyproject.toml` or `pytest.ini`) with `testpaths = ["tests"]` so root-level `cv_test.py` is never collected.
- `tests/conftest.py`:
  - Session-scoped fixture: one file-based SQLite database (via `tmp_path_factory`), `PRAGMA foreign_keys=ON`, `Base.metadata.create_all` run once.
  - Function-scoped `db_session` fixture: opens a connection + outer transaction, begins a nested SAVEPOINT-bound session, yields it, rolls back and closes after the test.
  - Function-scoped `client` fixture: `TestClient(app)` with `app.dependency_overrides[get_db]` pointed at `db_session`; override cleared after the test.
  - Generic, domain-agnostic helper(s) for an authenticated user without going through HTTP (e.g. `create_user(db_session, email, password) -> User`, `auth_headers(user) -> dict`), built directly against the DB and `auth.create_access_token`.
- One smoke test proving the harness itself works (app imports, `client.get("/openapi.json")` → 200, inside the isolated DB).

**Out of scope:** the missing Postgres driver, lint/type-checking, coverage thresholds, testing actual auth or CV endpoints.

### Unit 2 — Auth test suite
*Blocked by: Unit 1.*

Real HTTP flow via Unit 1's `client` fixture (no direct-DB shortcuts for the flows under test):

- `POST /auth/register`: success (201), duplicate email (400), invalid email format (422). The app currently accepts any non-empty password (no strength rule) — test documents this as current behavior, not a gap to fix.
- `POST /auth/login`: success returns a bearer token (200), wrong password (401), unknown email (401).
- `GET /users/me`: valid token (200), no `Authorization` header (401), malformed token string (401), expired token — crafted directly via `jose.jwt.encode` with a past `exp`, not by mutating `ACCESS_TOKEN_EXPIRE_MINUTES` (401), token whose `sub` references a nonexistent/deleted user (401).

**Out of scope:** password-strength validation, rate limiting, email verification.

### Unit 3 — CV CRUD + ownership test suite
*Blocked by: Unit 1.*

Uses Unit 1's direct-DB user/auth-header helpers for setup; exercises the six CV endpoints:

- Happy path: `POST /cv`, `GET /cv`, `GET /cv/{id}`, `PUT /cv/{id}`, `DELETE /cv/{id}`, `GET /cv/{id}/html`.
- Cross-user isolation: user B hitting user A's CV via get/update/delete/html → **404** (locks in the existing "don't leak existence" behavior as correct, per the code's own comments — not something to change).
- `id_user` in a create payload can't be spoofed — the CV is always attached to the authenticated caller.
- `GET /cv` returns only the caller's CVs; `[]` when none exist.
- `PUT` fully replaces nested children (missions, formations, projects/technologies, languages, activities, personal information) — verifies the documented delete-and-recreate strategy, not partial-update semantics.
- `DELETE` cascades to all child rows.
- All six CV endpoints reject unauthenticated requests with 401.

**Out of scope:** concurrency/race conditions, pagination, PATCH/partial-update semantics (not implemented), exhaustive technology-dedup edge cases.

### Unit 4 — CI integration
*Blocked by: Unit 2 and Unit 3.*

- `.github/workflows/tests.yml`: triggers on `push` to `main` and `pull_request` targeting `main`; `ubuntu-latest`; Python 3.10; installs `requirements.txt` + `requirements-dev.txt`; runs `pytest --cov` (report only, no enforced minimum).
- README: mark "Tests automatisés (pytest)" done in the Roadmap section; add a CI status badge alongside the existing badges.

**Out of scope:** lint/type-checking in this workflow, making the workflow a required branch-protection status check, coverage threshold gating, multi-version/OS test matrix, the missing Postgres driver.

## Deferred to later steps

- Writing the actual spec document/issue bodies — `/to-spec`.
- Filing the four GitHub issues with native dependency links and `ready-for-agent` labels — `/to-tickets` (also blocked here by `gh` not being available on this machine; will need to be resolved before that step can publish anything).
- Any implementation of the harness, tests, or CI workflow itself.
