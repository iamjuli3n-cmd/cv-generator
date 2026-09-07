# SQLite for the automated test database, not PostgreSQL

**Status**: accepted

The application runs on PostgreSQL in production, but the automated test suite (test harness, auth suite, CV/ownership suite — see the linked GitHub issues) runs against a file-based SQLite database instead, wrapped per-test in a SAVEPOINT that's rolled back afterward. We chose this because nothing in `models.py` uses Postgres-specific column types, Docker isn't available in this project's development environment, and a file-based SQLite database is fast enough to run on every push and pull request without a service container.

## Considered options

- **Real PostgreSQL** via a GitHub Actions service container (CI) and `docker-compose` (local dev): rejected as the default — slower per run, and requires Docker locally, which isn't set up for this project today.
- **`testcontainers-python`**: rejected for the same reason — still needs Docker, and adds a new test-only dependency for no fidelity gain given the current schema.

## Consequences

The suite doesn't exercise genuine PostgreSQL behavior — its specific constraint-violation error classes, JSON/array column types, or transaction-isolation quirks. A bug that only manifests against real Postgres can pass this suite. Revisit this decision if the schema starts relying on Postgres-specific features, or if Docker becomes available in CI/local dev and the fidelity gap starts costing real bugs.
