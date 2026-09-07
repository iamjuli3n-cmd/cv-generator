---
title: Automated testing foundation + CI integration
status: finalized — delivered as a local file, not a tracker issue (see Further Notes)
label: ready-for-agent
source: docs/interviews/automated-testing-foundation.md
---

## Problem Statement

The CV Generator API has no automated way to verify that authentication and CV ownership rules keep working as the codebase changes. A maintainer currently has to manually exercise registration, login, and every CV endpoint — including cross-account isolation — to catch a regression, and nothing stops a broken change from being merged, because no check runs automatically on a pull request or a push to `main`. A cross-account data leak, a broken login, or an accidentally-removed ownership filter would only be discovered in production, or not at all.

## Solution

Build a pytest-based automated test suite that exercises the API the same way a real client would — through HTTP, via FastAPI's `TestClient` — backed by an isolated test database so tests never touch real data and never leak state into each other. Cover the two areas with real security consequences first (authentication, and CV ownership boundaries), then wire the suite into GitHub Actions so it runs automatically on every push to `main` and every pull request targeting it, with a visible pass/fail signal.

## User Stories

1. As a maintainer, I want a reusable authenticated `TestClient` fixture, so that I can write API-level tests without repeating request/response boilerplate.
2. As a maintainer, I want each test to run against an isolated database, so that tests never leak state into each other or touch a real database.
3. As a maintainer, I want the test database to be created automatically when the suite runs, so that nobody has to provision a database by hand before running tests.
4. As a maintainer, I want a fixture that gives me an authenticated user without going through the HTTP registration flow, so that ownership tests can set up test data quickly and stay focused on what they're actually testing.
5. As a maintainer, I want a smoke test that proves the test harness itself works, so that a broken fixture is caught immediately instead of surfacing as confusing failures across unrelated suites.
6. As a maintainer, I want the test suite to run without a real PostgreSQL database or any environment configuration, so that anyone can clone the repo and run tests immediately.
7. As a maintainer, I want a test verifying that registering with a new email succeeds, so that the registration endpoint's happy path is provably correct.
8. As a maintainer, I want a test verifying that registering with an already-used email is rejected, so that duplicate accounts can never be created.
9. As a maintainer, I want a test verifying that registering with an invalid email format is rejected, so that malformed data never reaches the database.
10. As a maintainer, I want a test verifying that logging in with correct credentials returns a usable bearer token, so that the authentication flow is provably correct end-to-end.
11. As a maintainer, I want a test verifying that logging in with a wrong password is rejected, so that credential checking can't silently break.
12. As a maintainer, I want a test verifying that logging in with an unknown email is rejected, so that the login endpoint's failure path is covered.
13. As a maintainer, I want a test verifying that a valid token grants access to the current-user endpoint, so that token-based authentication works end-to-end.
14. As a maintainer, I want a test verifying that a request with no `Authorization` header is rejected, so that protected endpoints can never be reached anonymously.
15. As a maintainer, I want a test verifying that a malformed token is rejected, so that broken or tampered tokens never authenticate.
16. As a maintainer, I want a test verifying that an expired token is rejected, so that tokens can't be used past their intended lifetime.
17. As a maintainer, I want a test verifying that a token referencing a deleted or nonexistent user is rejected, so that stale tokens can't authenticate as a user who no longer exists.
18. As a maintainer, I want a test verifying that an authenticated user can create a CV with all of its nested sections, so that the create flow is provably correct end-to-end.
19. As a maintainer, I want a test verifying that a user can list their own CVs, so that the read-all endpoint reflects only what they own.
20. As a maintainer, I want a test verifying that a user with no CVs gets an empty list rather than an error, so that the empty state is handled correctly.
21. As a maintainer, I want a test verifying that a user can fetch one of their own CVs by id with all nested data intact, so that the read-one endpoint and its eager-loading logic are correct.
22. As a maintainer, I want a test verifying that updating a CV fully replaces its nested sections, so that the documented delete-and-recreate update strategy behaves as intended.
23. As a maintainer, I want a test verifying that a user can delete their own CV, so that the delete endpoint works as expected.
24. As a maintainer, I want a test verifying that deleting a CV also removes all of its nested child records from the database, so that no orphaned data is left behind.
25. As a maintainer, I want a test verifying that a user can render one of their own CVs as HTML, so that the preview endpoint works end-to-end.
26. As a maintainer, I want a test verifying that one user cannot read another user's CV, so that a cross-account data leak would be caught automatically.
27. As a maintainer, I want a test verifying that one user cannot update another user's CV, so that cross-account tampering would be caught automatically.
28. As a maintainer, I want a test verifying that one user cannot delete another user's CV, so that cross-account data destruction would be caught automatically.
29. As a maintainer, I want a test verifying that one user cannot render another user's CV as HTML, so that the preview endpoint can't leak another user's data.
30. As a maintainer, I want the cross-user-access tests to assert a 404 (not a 403), so that the deliberate "don't reveal existence" behavior is locked in and can't be silently reverted to something that leaks whether a CV id exists.
31. As a maintainer, I want a test verifying that a user cannot assign a new CV to someone else's account by supplying a different `id_user` in the request body, so that ownership can never be spoofed on creation.
32. As a maintainer, I want a test verifying that every CV endpoint rejects unauthenticated requests with a 401, so that the API can never be reached anonymously.
33. As a contributor, I want the test suite to run automatically on every pull request, so that I get fast feedback before a maintainer reviews my change.
34. As a maintainer, I want the test suite to run automatically on every push to `main`, so that regressions on the main branch are caught immediately.
35. As a contributor, I want a coverage report generated by CI, so that I can see which parts of my change are untested.
36. As a visitor to the repository, I want a CI status badge in the README, so that I can immediately tell whether the project's tests are currently passing.
37. As a maintainer, I want the README's roadmap to accurately reflect that automated tests now exist, so that the documentation doesn't misrepresent the project's state.

## Implementation Decisions

**Test database & isolation**
- The suite runs against a file-based SQLite database, not PostgreSQL — recorded as an ADR, since production runs on Postgres and this is a deliberate fidelity/speed trade-off (see Further Notes).
- One SQLite database file is created for the whole test session; its schema is created once. Each individual test runs inside its own SAVEPOINT-based nested transaction, rolled back after the test completes — full isolation between tests without rebuilding the schema each time.
- Foreign-key enforcement is turned on for the test connection, for closer parity with Postgres's default behavior.

**Making the app testable**
- The database configuration currently builds its SQLAlchemy engine and session factory eagerly, at import time, by reading a required connection-string environment variable. This is refactored so the engine and session factory are built lazily, on first use, behind small accessor functions — same environment-variable-driven configuration style as today, no application-factory rewrite. This removes an import-time crash that would otherwise occur whenever that environment variable isn't set.
- Because the FastAPI dependency that yields a database session is overridden per-test to point at the isolated test database, the production database configuration is never actually exercised during a test run — so the test suite needs no real connection string at all.

**Test harness & fixtures**
- A per-test fixture yields an isolated, transaction-scoped database session (see above).
- A per-test fixture provides an HTTP test client wired to use that isolated session in place of the real database dependency.
- A generic, domain-agnostic fixture/helper creates a user directly in the test database and mints a valid access token for them, without going through the HTTP registration/login flow — for any test that just needs "a logged-in user" as setup rather than as the thing under test.
- One smoke test exercises the harness itself (an authenticated or public request succeeding against the isolated database) as an independent acceptance signal, separate from the auth and CV suites that build on it.

**Dependency & tooling boundaries**
- Test-only dependencies (the test framework, a coverage plugin, and the HTTP client library the test client needs) are declared separately from the application's runtime dependencies, so a production install never pulls in test tooling.
- Test configuration restricts test discovery to the dedicated test directory, so the existing sample-CV fixture-data module at the repository root — which happens to match the test framework's default file-naming pattern but contains no actual tests — is never mistakenly collected.

**CI**
- A GitHub Actions workflow runs on every push to `main` and every pull request targeting `main`, on a single Linux runner, using Python 3.10.
- It installs both the runtime and test dependency sets, then runs the test suite with coverage reporting enabled. No minimum coverage percentage is enforced.
- The workflow is not configured as a required status check for merging yet.
- The README is updated to mark automated tests as delivered in its roadmap, and gains a CI status badge alongside its existing badges.

## Testing Decisions

- A good test in this suite exercises the API exactly as an external client would — through the real HTTP routes, asserting on status codes and response bodies — rather than calling internal functions directly or asserting on internal implementation details. The one narrow exception: confirming that deleting a CV removes its child rows requires a direct query against the test database session, since the API itself exposes no way to observe "this row no longer exists" once its parent is gone.
- Two modules of behavior get full test coverage: authentication (registration, login, current-user lookup) and CV CRUD together with ownership enforcement (create, list, read, update, delete, HTML rendering, and cross-account isolation on all of them).
- There is no prior art for this in the codebase — no test suite exists today. The one file that might look like prior art, a module holding a fully-populated sample CV object, is fixture data for manual/demo use, not a test, and should not be treated as a pattern to follow.

## Out of Scope

- Fixing the missing PostgreSQL driver dependency (the app requires Postgres in production but the driver isn't declared) — a pre-existing gap, tracked separately.
- Linting or type-checking in CI.
- Enforcing a minimum coverage percentage.
- Making the CI workflow a required branch-protection status check.
- Testing across multiple Python versions or operating systems.
- Partial-update (PATCH) semantics for CVs — the API only supports full replacement today.
- Concurrency/race-condition testing, pagination, and exhaustive technology-deduplication edge cases.
- Renaming the existing sample-CV fixture-data module.

## Further Notes

- This spec covers all of the work as one initiative. A separate ticket-breakdown step will split it into four sequenced units — test harness & fixtures; auth suite; CV CRUD & ownership suite; CI integration — with the harness blocking both test suites, and CI integration blocked by both suites (so a green CI badge is never shown before real test coverage exists).
- The SQLite-vs-Postgres decision is recorded as `docs/adr/0001-sqlite-for-test-database.md`.
- The full interview record behind this spec, including facts discovered about the codebase and the rationale for every decision, is at `docs/interviews/automated-testing-foundation.md`.
- **Delivered as a local file, not a tracker issue.** This repo's convention (per its own agent docs) is to track specs as GitHub issues via the `gh` CLI, but `gh` isn't installed/on `PATH` on this machine, and the decision was made to use local files for now rather than wait on that. This file is the specification of record until it's carried over to the tracker; the content is unchanged from what would be published, so no rework is needed if/when that happens.
