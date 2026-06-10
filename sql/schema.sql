-- Schema for data/statsapi/statsapi.duckdb
--
-- Tables mirror the dataframely schemas in transform.py. The parquet files
-- under data/statsapi/ are an intermediate form; this database is the serving
-- store. CREATE OR REPLACE keeps the load step idempotent across marimo reruns.

CREATE OR REPLACE TABLE main.sports (
    sport_id   UINTEGER NOT NULL,
    sport_code TEXT     UNIQUE NOT NULL,
    sport_name TEXT     UNIQUE NOT NULL,
    sport_abbr TEXT     UNIQUE NOT NULL,
    sort_order UINTEGER UNIQUE NOT NULL,
    sport_link TEXT     UNIQUE NOT NULL,
    CONSTRAINT pk_sports PRIMARY KEY (sport_id),
    CONSTRAINT sport_link_regex
        CHECK (sport_link ~ '/api/v\d(?:\.\d)?((?:/[a-zA-Z0-9]+)+)')
);

CREATE OR REPLACE TABLE main.seasons (
    season    UINTEGER NOT NULL,
    league_id UINTEGER NOT NULL,
    sport_id  UINTEGER NOT NULL,
    n_games   UINTEGER NOT NULL,
    n_teams   UINTEGER NOT NULL,
    -- composite key: a (league, season, sport) triple is unique, not each column
    CONSTRAINT pk_seasons PRIMARY KEY (season, league_id, sport_id)
);

-- TODO (#5 load): leagues, divisions, division_seasons, teams, team_seasons
-- follow the remaining schemas in transform.py.
