-- Schema for data/statsapi/statsapi.duckdb
--
-- Tables mirror the dataframely schemas in transform.py (column names,
-- nullability, and keys). The parquet files under data/statsapi/ are an
-- intermediate form; this database is the serving store. CREATE OR REPLACE
-- keeps the load step idempotent across marimo reruns.
--
-- link columns share the same shape; the regex is repeated per table because
-- DuckDB CHECK constraints cannot reference a shared expression.

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

CREATE OR REPLACE TABLE main.leagues (
    league_id   UINTEGER NOT NULL,
    league_name TEXT     NOT NULL,
    league_abbr TEXT     UNIQUE NOT NULL,
    last_season UINTEGER NOT NULL,
    is_active   BOOLEAN  NOT NULL,
    sort_order  UINTEGER UNIQUE NOT NULL,
    league_link TEXT     UNIQUE NOT NULL,
    CONSTRAINT pk_leagues PRIMARY KEY (league_id),
    CONSTRAINT league_link_regex
        CHECK (league_link ~ '/api/v\d(?:\.\d)?((?:/[a-zA-Z0-9]+)+)')
);

CREATE OR REPLACE TABLE main.seasons (
    league_id         UINTEGER NOT NULL,
    season            UINTEGER NOT NULL,
    sport_id          UINTEGER NOT NULL,
    n_games           UINTEGER NOT NULL,
    n_teams           UINTEGER NOT NULL,
    has_divisions     BOOLEAN  NOT NULL,
    has_split_season  BOOLEAN  NOT NULL,
    n_wildcard_teams  UINTEGER NOT NULL,
    pre_start         DATE     NOT NULL,
    pre_end           DATE     NOT NULL,
    spring_start      DATE,
    spring_end        DATE,
    season_start      DATE     NOT NULL,
    regular_start     DATE     NOT NULL,
    first_half_end    DATE,
    all_star_game     DATE,
    second_half_start DATE,
    regular_end       DATE     NOT NULL,
    post_start        DATE,
    post_end          DATE,
    season_end        DATE     NOT NULL,
    off_start         DATE     NOT NULL,
    off_end           DATE,
    -- a (league, season, sport) triple is unique, not each column
    CONSTRAINT pk_seasons PRIMARY KEY (season, league_id, sport_id)
);

CREATE OR REPLACE TABLE main.divisions (
    division_id   UINTEGER NOT NULL,
    division_name TEXT     UNIQUE NOT NULL,
    league_id     UINTEGER NOT NULL,
    is_active     BOOLEAN  NOT NULL,
    division_link TEXT     UNIQUE NOT NULL,
    CONSTRAINT pk_divisions PRIMARY KEY (division_id, league_id),
    CONSTRAINT division_link_regex
        CHECK (division_link ~ '/api/v\d(?:\.\d)?((?:/[a-zA-Z0-9]+)+)')
);

CREATE OR REPLACE TABLE main.division_seasons (
    division_id UINTEGER NOT NULL,
    season      UINTEGER NOT NULL,
    CONSTRAINT pk_division_seasons PRIMARY KEY (division_id, season)
);

CREATE OR REPLACE TABLE main.teams (
    team_id   UINTEGER NOT NULL,
    team_link TEXT     UNIQUE NOT NULL,
    is_active BOOLEAN  NOT NULL,
    CONSTRAINT pk_teams PRIMARY KEY (team_id),
    CONSTRAINT team_link_regex
        CHECK (team_link ~ '/api/v\d(?:\.\d)?((?:/[a-zA-Z0-9]+)+)')
);

CREATE OR REPLACE TABLE main.team_seasons (
    team_id          UINTEGER NOT NULL,
    season           UINTEGER NOT NULL,
    team_name        TEXT     NOT NULL,
    team_code        TEXT     NOT NULL,
    league_id        INTEGER  NOT NULL,  -- signed: -1 marks unaffiliated teams
    sport_id         UINTEGER NOT NULL,
    division_id      UINTEGER,
    location_name    TEXT,
    venue_id         UINTEGER,
    spring_league_id UINTEGER,
    spring_venue_id  UINTEGER,
    parent_org_id    UINTEGER,
    CONSTRAINT pk_team_seasons PRIMARY KEY (team_id, season, league_id)
);
