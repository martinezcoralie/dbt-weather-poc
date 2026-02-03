# CI/CD (Appendix)

This repo uses GitHub Actions for CI and dbt docs publishing.

CI jobs (high-level):

- Lint Python with Ruff.
- Ingest sample data from the Météo-France API and run `dbt deps` + `dbt build`
  on DuckDB.
- Smoke test Docker Compose (`app` + `prefect-server`).
- Publish dbt docs to GitHub Pages.

Required secret:

- `METEOFRANCE_TOKEN` (used by the ingestion + dbt build job)

If you fork/clone and keep CI enabled, set this secret in your repository
settings, or disable the ingestion job.

Token setup guide: `docs/appendix/api-access.md`.
