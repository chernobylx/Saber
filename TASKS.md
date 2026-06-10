# Tasks — Saber

MLB Stats API → polars/dataframely ETL. Parquet files under `data/statsapi/`
are an **intermediate** form; the goal is to load all data into
`data/statsapi/statsapi.duckdb` as the serving store.

## 🔄 In Progress

## 📋 Backlog
<!-- ordered by priority: top = next up -->
- [ ] Write README.md — purpose, setup (`pixi install`), how to run the ETL
      marimo app, data-source/reproducibility note (data/statsapi is regenerable
      from extract.py)
- [ ] Finish the DuckDB load step in ETL.py (end goal) — DDL now lives in
      sql/schema.sql (sports + seasons done; leagues/divisions/division_seasons/
      teams/team_seasons still TODO there). Write all validated frames into
      statsapi.duckdb. Clear the residual ETL.py lint findings as part of this
      (F841 LC, import sort/E501 in the load cells, B018 SeasonSchema scratch)

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
