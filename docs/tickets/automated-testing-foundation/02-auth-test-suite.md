---
ticket: 02
title: Auth test suite
status: ready-for-agent
spec: docs/specs/automated-testing-foundation.md
---

# 02: Auth test suite

## Goal

Automated proof that registration, login, and current-user lookup behave correctly and reject invalid credentials/tokens, so a future change to `auth.py` or the `/auth/*` and `/users/me` routes in `main.py` can't silently break authentication without a test failing.

## Scope

Create `tests/test_auth.py`, using Ticket 01's `client` fixture exclusively — every test in this file goes through the real HTTP endpoints, since that's what's under test here:

- `POST /auth/register`:
  - A new email → 201, response body matches the `UserOut` shape (no password field present).
  - An already-registered email → 400.
  - A syntactically invalid email → 422.
- `POST /auth/login` (form-encoded body per `OAuth2PasswordRequestForm`: `username` = email, `password` = password):
  - Correct credentials → 200, response contains `access_token` and `token_type`.
  - Correct email with the wrong password → 401.
  - An email that was never registered → 401.
- `GET /users/me`:
  - A valid bearer token (obtained via a prior register/login call in the test) → 200, body reflects the correct user.
  - No `Authorization` header → 401.
  - A syntactically invalid bearer token string → 401.
  - A token with an `exp` claim already in the past — built directly with `jose.jwt.encode` using the same `SECRET_KEY`/`ALGORITHM` as `auth.py`, not by mutating `auth.ACCESS_TOKEN_EXPIRE_MINUTES` — → 401.
  - A well-formed, unexpired token whose `sub` claim is a user id that does not exist in the test database → 401.

Note: the app currently accepts any non-empty password with no strength rule. Do not add such validation, and do not write a test asserting stronger behavior than exists — this is documented current behavior, not a gap this ticket fixes.

## Acceptance Criteria

- [ ] Every scenario listed in Scope has a corresponding passing test.
- [ ] Every test in this file drives the app through the real HTTP endpoints via the `client` fixture — none calls `auth.py` functions directly to bypass the API.
- [ ] The expired-token test constructs its token with `jose.jwt.encode` directly; it does not monkeypatch `ACCESS_TOKEN_EXPIRE_MINUTES`.
- [ ] `pytest tests/test_auth.py` passes standalone, and the full `pytest` run still passes.

## Relevant Context/Files

- `main.py` — route handlers for `POST /auth/register`, `POST /auth/login`, `GET /users/me`. Note `/auth/login` takes form data (`OAuth2PasswordRequestForm`), not JSON.
- `auth.py` — `hash_password`/`verify_password` (bcrypt via passlib), `create_access_token`/`get_current_user` (JWT via `python-jose`), `SECRET_KEY` (env var with a fallback default), `ALGORITHM = "HS256"`, `ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24`.
- `classCV.py` — `UserCreate` (`email`, `password`), `UserOut` (`id_user`, `email`, `is_active`), `Token` (`access_token`, `token_type`) — the request/response shapes to assert against.
- `models.py` — `User` model fields, useful for constructing the "token references a nonexistent user id" scenario (e.g. by picking an id known not to exist, or by deleting the user via `db_session` after issuing the token).
- Ticket 01's harness — the `client` fixture; `db_session` is only needed here if a test wants to inspect or manipulate a `User` row directly for an edge case (e.g. the nonexistent-user-id token).

## Blocked By

Ticket 01 (Test harness + fixtures).

## Why That Blocking Edge Is Real

Every scenario in this ticket needs an isolated HTTP client backed by an isolated database. Without Ticket 01, tests would either share one real (or accidentally-real) database across runs — making a "duplicate email" test's outcome depend on what a previous run left behind — or the test process would crash immediately on `import main`, because `database.py` currently builds its engine eagerly from a `DATABASE_URL` that may not be set in a test environment. There is no way to write or run a single test in this ticket before that fixture and the import-time fix exist.

## What Would Break If Attempted In The Opposite Order

Writing this suite before Ticket 01 exists means either every test pollutes and depends on shared, real database state (so "register with a new email" could fail on a second run because the email is no longer new), or the test process fails to even start, since `database.py`'s current eager engine construction raises immediately when `DATABASE_URL` is absent. Either way, the suite would be flaky or entirely non-functional from the first test written, and would need to be rewritten from scratch once Ticket 01 lands anyway.
