---
ticket: 04
title: CI integration
status: ready-for-agent
spec: docs/specs/automated-testing-foundation.md
---

# 04: CI integration

## Goal

Every push to `main` and every pull request targeting `main` automatically runs the full test suite on GitHub Actions, with a visible, accurate signal — coverage report, CI badge, updated README — so a broken auth or CV/ownership change surfaces before a human has to notice it manually.

## Scope

- Add a GitHub Actions workflow file that:
  - Triggers on `push` to `main` and `pull_request` targeting `main`.
  - Runs on `ubuntu-latest`.
  - Sets up Python 3.10.
  - Installs both `requirements.txt` and `requirements-dev.txt`.
  - Runs the test suite with coverage reporting (e.g. `pytest --cov`); coverage is reported, not gated — no minimum-percentage threshold, no failure on low coverage.
- Update `README.md`:
  - Check off "Tests automatisés (pytest)" in the Roadmap section.
  - Add a CI status badge for the new workflow, alongside the existing Python/FastAPI/PostgreSQL/License badges at the top of the file.

## Acceptance Criteria

- [ ] The workflow runs on a push to `main` and on a pull request targeting `main`.
- [ ] The workflow fails if any test fails, and succeeds when Tickets 02 and 03's suites (and Ticket 01's smoke test) all pass.
- [ ] The workflow does not enforce a minimum coverage percentage and does not run any linter or type-checker.
- [ ] The workflow is not configured as a required branch-protection status check.
- [ ] The README shows a CI badge reflecting the workflow's real status, and the Roadmap's "Tests automatisés (pytest)" line is checked.

## Relevant Context/Files

- No `.github/workflows/` directory exists yet — this ticket creates it.
- `requirements.txt` (runtime dependencies) and `requirements-dev.txt` (from Ticket 01: `pytest`, `pytest-cov`, `httpx`) — both must be installed in the workflow.
- `README.md` — the Roadmap section currently lists "Tests automatisés (pytest)" as unchecked; the badge row at the top currently has Python/FastAPI/PostgreSQL/License badges, to which the CI badge is added.
- `docs/specs/automated-testing-foundation.md` — confirms report-only coverage (no gate), not-yet-required status check, and tests-only scope (no lint/type-check) are deliberate, spec'd exclusions for this ticket, not oversights.

## Blocked By

Ticket 02 (Auth test suite) and Ticket 03 (CV CRUD + ownership test suite).

## Why That Blocking Edge Is Real

This ticket's own acceptance criteria require the workflow to succeed when Tickets 02 and 03's suites all pass — that's only checkable once those suites exist. More importantly, the README update this ticket makes ("Tests automatisés (pytest)" done, plus a green CI badge) is a factual claim about the repository's state. Making that claim before Tickets 02 and 03 exist would be true of nothing more than Ticket 01's single smoke test, which is not what "automated tests" means to anyone reading the README.

## What Would Break If Attempted In The Opposite Order

A CI workflow wired up before Tickets 02 and 03 exist would go green on essentially zero real coverage (just Ticket 01's smoke test), while the README would claim — falsely — that the project has automated test coverage and passing CI, when auth and CV/ownership behavior actually have no tests yet. Anyone trusting that badge or that roadmap checkbox would be misled about the real safety net in place.
