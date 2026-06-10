# Tasks — Saber

MLB Stats API → polars/dataframely ETL. Parquet files under `data/statsapi/`
are an **intermediate** form; the goal is to load all data into
`data/statsapi/statsapi.duckdb` as the serving store.

## 🔄 In Progress

## 📋 Backlog
<!-- ordered by priority: top = next up -->
<!-- empty — core ETL is complete; add analysis/query work here next -->

## ✅ Done
- [x] Set up dev tooling — `[tasks]` in pixi.toml (lint/format/typecheck/
      test/check) + ruff/ty/pytest config in pyproject.toml (py313, flat
      layout; ruff/ty respect .gitignore so .pixi/data are skipped) (2026-06-10)
- [x] Project organization — cleaned extract.py/transform.py to zero lint+type
      findings (collections.abc.Callable, dict|None defaults, SIM108, dropped
      no-op try/except); added tests/ package; deleted stale extract.ipynb;
      moved DDL into sql/schema.sql (fixed seasons composite PK, verified it
      executes in duckdb) and wired ETL.py to load it via the db connection.
      ty fully passes (2026-06-10)
- [x] Tests for the transform layer — 15 pytest tests covering each transform_*
      against its dataframely schema plus normalization logic, and the
      Collection integrity rules; synthetic fixtures, no network. ty clean
      (2026-06-10)
- [x] Write README.md — purpose, setup, how to run the marimo ETL app, project
      structure, reproducibility note (2026-06-10)
- [x] DuckDB load — full DDL for all 7 tables in sql/schema.sql (derived from
      the dataframely schemas); ETL.py load cell (re)creates tables and inserts
      the integrity-checked frames idempotently (CREATE OR REPLACE + INSERT BY
      NAME). Verified end-to-end against real parquet: statsapi.duckdb populated
      (sports 14, leagues 118, seasons 924, divisions 89, division_seasons 1795,
      teams 2143, team_seasons 30052). pixi run check is green (2026-06-10)
