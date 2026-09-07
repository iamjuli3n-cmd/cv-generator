---
ticket: 03
title: CV CRUD + ownership test suite
status: ready-for-agent
spec: docs/specs/automated-testing-foundation.md
---

# 03: CV CRUD + ownership test suite

## Goal

Automated proof that CV CRUD works end-to-end and that CV ownership is enforced everywhere — one user's CVs are provably invisible and untouchable by another user — so a future change to the `/cv` routes in `main.py` can't silently reintroduce a cross-account data leak or break the CRUD flows.

## Scope

Create `tests/test_cv_crud.py`, using Ticket 01's `client`/`db_session` fixtures plus its `create_user`/`auth_headers` helpers to set up two distinct users directly in the database (no HTTP registration round-trip for setup — that's Ticket 02's territory):

- **Happy path**, as one authenticated user:
  - `POST /cv` with a full nested payload (personal information, at least one experience with a mission, one formation, one project with a technology, one language, one activity with an activity mission) → 201, response mirrors the input.
  - `GET /cv` → list containing that CV.
  - `GET /cv/{id}` → the same CV with all nested sections intact.
  - `PUT /cv/{id}` with a different nested payload → 200; a follow-up `GET /cv/{id}` shows only the new nested data (assert the old mission/technology/etc. content no longer appears anywhere in the response, proving the old rows were replaced, not merged).
  - `DELETE /cv/{id}` → success response; a follow-up `GET /cv/{id}` → 404; querying `db_session` directly afterward confirms no `Experience`, `Mission`, `Formation`, `Project`, `ProjectTechnology`, `Language`, `Activity`, `ActivityMission`, or `PersonnalInformation` rows remain for that `id_cv`.
  - `GET /cv/{id}/html` → 200, with the CV's data reflected in the rendered HTML.
- **Empty state**: a freshly created user with no CVs → `GET /cv` returns `[]`.
- **Ownership isolation**: user B, authenticated, attempts `GET /cv/{id}`, `PUT /cv/{id}`, `DELETE /cv/{id}`, and `GET /cv/{id}/html` on a CV created by user A → **404** in every case (not 403 — this is the documented, intentional "don't reveal existence" behavior; assert 404 explicitly so a future change to 403 fails this test rather than passing silently).
- **Ownership spoofing**: user A calls `POST /cv` with an `id_user`-like field in the payload pointing at user B (if the schema accepts such a field at all) → the created CV is attached to user A, the authenticated caller, never to the spoofed target — verify by checking `GET /cv` as user A (present) and as user B (absent).
- **Unauthenticated access**: each of the six CV endpoints, called with no `Authorization` header → 401.

## Acceptance Criteria

- [ ] Every scenario listed in Scope has a corresponding passing test.
- [ ] Ownership-isolation tests assert 404 specifically, with a test name or comment making clear this is intentional behavior being locked in, not an oversight.
- [ ] The cascade-delete test queries `db_session` directly to confirm child rows are gone; a 404 on the follow-up `GET` alone is not accepted as proof.
- [ ] Test setup (creating the two users) uses Ticket 01's direct-DB helpers, not `/auth/register` + `/auth/login`.
- [ ] `pytest tests/test_cv_crud.py` passes standalone, and the full `pytest` run still passes.

## Relevant Context/Files

- `main.py` — all six CV routes: `POST /cv`, `GET /cv`, `GET /cv/{id_cv}`, `PUT /cv/{id_cv}`, `DELETE /cv/{id_cv}`, `GET /cv/{id_cv}/html`, plus the `_db_cv_to_schema` helper that shapes responses. The code's own comments in `update_cv`, `delete_cv`, `render_cv_html`, and `get_cv` mark the `id_user` filter as a previously-missing security fix — this ticket is what locks that behavior in with a test, so it can't regress silently.
- `models.py` — full schema: `CV`, `PersonnalInformation`, `Experience`, `Mission`, `Formation`, `Project`, `Technology`, `ProjectTechnology`, `Language`, `Activity`, `ActivityMission`, cascading via `cascade="all, delete-orphan"` from `CV`/`Experience`/`Activity`. This is what the cascade-delete test verifies at the row level.
- `classCV.py` — the full `CV` Pydantic schema and its nested schemas, which request/response bodies must match.
- `docs/adr/0001-sqlite-for-test-database.md` and `docs/specs/automated-testing-foundation.md` — confirm the direct-DB-query seam for cascade verification, and the 404-not-403 assertion, are intentional, spec'd decisions, not this ticket's own invention.
- Ticket 01's harness: `client`, `db_session`, `create_user`, `auth_headers`.

## Blocked By

Ticket 01 (Test harness + fixtures).

## Why That Blocking Edge Is Real

This suite needs two independently-authenticated users and an isolated database to prove cross-account isolation. Without Ticket 01's `create_user`/`auth_headers` helpers, setting up "two logged-in users" means either duplicating that fixture logic inside this ticket or routing through `/auth/register` + `/auth/login` for every test — slower, and re-testing Ticket 02's territory instead of this suite's own. Without the isolated `db_session`, the cascade-delete assertions have no database to query directly, and without the lazy-engine fix, the test process may not even import successfully.

## What Would Break If Attempted In The Opposite Order

Without Ticket 01, this suite would either invent its own throwaway user/session/client setup — which then has to be discarded and rewritten against Ticket 01's fixtures once they exist, duplicating work — or run against a real, shared database, where one test's leftover CV rows could make another test's "user has no CVs" or "list contains only my CVs" assertions fail nondeterministically depending on run order.
