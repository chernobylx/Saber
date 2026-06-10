# Saber

An ETL pipeline that extracts baseball reference data from the MLB Stats API
(`statsapi.mlb.com`), normalizes and validates it with **polars** +
**dataframely**, and loads it into a **DuckDB** database for analysis.

The parquet files under `data/statsapi/` are an intermediate cache; the goal is
a clean, constraint-checked `statsapi.duckdb` as the serving store.

## Setup

```bash
# Install pixi if needed: https://pixi.sh
pixi install
```

## Usage

The pipeline is a [marimo](https://marimo.io) app. Open it interactively:

```bash
pixi run marimo edit ETL.py
```

Running the notebook will, in order:

1. **Extract** — download any missing endpoint to `data/statsapi/<table>.parquet`
   (`sports`, `leagues`, `divisions`, `seasons`, `teams`). HTTP responses are
   cached on disk (joblib) under `.cache/`, so re-runs don't re-hit the API.
2. **Transform** — normalize the raw JSON into tidy tables (`transform.py`).
3. **Validate** — enforce per-table schemas and cross-table integrity with
   dataframely (`*Schema`, `SportsSeasons`, `LeagueCollection`).
4. **Load** — create the DuckDB tables from `sql/schema.sql`. *(In progress —
   see TASKS.md.)*

## Project Structure

| Path | Purpose |
|---|---|
| `extract.py` | Cached MLB Stats API client; one function per endpoint, returns polars LazyFrames |
| `transform.py` | `transform_*` normalization functions + dataframely schemas/collections |
| `ETL.py` | marimo app wiring extract → transform → validate → load |
| `sql/schema.sql` | DuckDB DDL, mirroring the dataframely schemas |
| `tests/` | pytest suite for the transform layer (synthetic data, no network) |
| `data/statsapi/` | Intermediate parquet cache + `statsapi.duckdb` (gitignored) |

## Reproducibility

`data/` and `.cache/` are gitignored. They are fully regenerable: running
`ETL.py` re-downloads any missing parquet from `statsapi.mlb.com` via
`extract.py`. No raw data needs to be committed or downloaded by hand.

## Development

```bash
pixi run check       # lint + typecheck + test
pixi run format      # auto-format with ruff
pixi run lint        # ruff check
pixi run typecheck   # ty check
pixi run test        # pytest
```
