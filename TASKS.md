# Tasks — Saber

MLB Stats API → polars/dataframely ETL. Parquet files under `data/statsapi/`
are an **intermediate** form; the goal is to load all data into
`data/statsapi/statsapi.duckdb` as the serving store.

## 🔄 In Progress

## 📋 Backlog
<!-- ordered by priority: top = next up -->
- [ ] Project organization — create `tests/`; move the inline `mo.sql` DDL out
      of ETL.py into `sql/`; remove the no-op `try/except: raise` blocks in
      extract.py and transform.py; remove or migrate the stale
      `extract.ipynb` (duplicates ETL.py/extract.py extract logic). Clear the
      easy lint/type findings along the way: `query: dict | None = None` in
      extract.py (×3), SIM108 ternary, B905 `zip(strict=)`
- [ ] Add pytest tests for `transform_*` functions and schema validation —
      build small synthetic raw frames, assert transformed output passes the
      dataframely schemas (SportSchema, LeagueSchema, SeasonSchema,
      DivisionSchema, TeamSchema, etc.) and the Collection filters
- [ ] Write README.md — purpose, setup (`pixi install`), how to run the ETL
      marimo app, data-source/reproducibility note (data/statsapi is regenerable
      from extract.py)
- [ ] Finish the DuckDB load step in ETL.py (end goal) — write all validated
      frames (sports, leagues, seasons, divisions, division_seasons, teams,
      team_seasons) into statsapi.duckdb. Fix the seasons DDL (currently every
      column is UNIQUE; composite PK should be season + league_id + sport_id)

## ✅ Done
- [x] Set up dev tooling — `[tasks]` in pixi.toml (lint/format/typecheck/
      test/check) + ruff/ty/pytest config in pyproject.toml (py313, flat
      layout; ruff/ty respect .gitignore so .pixi/data are skipped) (2026-06-10)
