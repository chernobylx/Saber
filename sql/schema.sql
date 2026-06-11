-- Schema for data/statsapi/statsapi.duckdb
--
-- Tables mirror the dataframely schemas in transform.py (column names,
-- nullability, and keys). The parquet files under data/statsapi/ are an
--
-- link columns share the same shape; the regex is repeated per table because
Begin Transaction;

CREATE SCHEMA IF NOT EXISTS api;

CREATE DOMAIN API_LINK as TEXT
    CHECK (VALUE ~ '/api/v\d(?:\.\d)?((?:/[a-zA-Z0-9]+)+)');


CREATE TABLE api.sports (
    sport_id    INTEGER CHECK (sport_id>=0) NOT NULL,
    sport_code  TEXT     UNIQUE NOT NULL,
    sport_name  TEXT     UNIQUE NOT NULL,
    sport_abbr TEXT     UNIQUE NOT NULL,
    sort_order INTEGER CHECK (sort_order>=0) UNIQUE NOT NULL,
    sport_link API_LINK     UNIQUE NOT NULL,
    --------------------------------------------
    CONSTRAINT pk_sports PRIMARY KEY (sport_id)
);

CREATE TABLE api.leagues (
    league_id INTEGER CHECK (league_id>=0) NOT NULL,
    league_name TEXT     NOT NULL,
    league_abbr TEXT     UNIQUE NOT NULL,
    last_season INTEGER CHECK (last_season>=0) NOT NULL,
    is_active   BOOLEAN  NOT NULL,
    sort_order INTEGER CHECK (sort_order>=0) UNIQUE NOT NULL,
    league_link API_LINK     UNIQUE NOT NULL,
    ---------------------------------------------
    CONSTRAINT pk_leagues PRIMARY KEY (league_id)
);

CREATE TABLE api.teams (
    team_id INTEGER CHECK (team_id>=0) NOT NULL,
    team_link API_LINK     UNIQUE NOT NULL,
    is_active BOOLEAN  NOT NULL,
    CONSTRAINT pk_teams PRIMARY KEY (team_id)
);


CREATE TABLE api.seasons (
    season_id INTEGER PRIMARY KEY,
    league_id INTEGER NOT NULL REFERENCES api.leagues (league_id),
    year INTEGER CHECK (year>=0) NOT NULL,
    sport_id INTEGER NOT NULL REFERENCES api.sports (sport_id),
    n_games INTEGER CHECK (n_games>=0) NOT NULL,
    n_teams INTEGER CHECK (n_teams>=0) NOT NULL,
    has_divisions     BOOLEAN  NOT NULL,
    has_split_season  BOOLEAN  NOT NULL,
    n_wildcard_teams INTEGER CHECK (n_wildcard_teams>=0) NOT NULL,
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
    CONSTRAINT unique_season_league_sport  UNIQUE (year, league_id, sport_id)
);

CREATE TABLE api.divisions (
    division_id INTEGER CHECK (division_id>=0) UNIQUE NOT NULL PRIMARY KEY,
    division_name TEXT     UNIQUE NOT NULL,
    league_id INTEGER  NOT NULL REFERENCES api.leagues (league_id),
    is_active     BOOLEAN  NOT NULL,
    division_link API_LINK     UNIQUE NOT NULL
);


CREATE TABLE api.team_seasons (
    team_id INTEGER NOT NULL REFERENCES api.teams (team_id),
    season_id INTEGER NOT NULL REFERENCES api.seasons (season_id),
    division_id INTEGER not null references api.divisions  (division_id),
    team_name        TEXT     NOT NULL,
    team_code        TEXT     NOT NULL,
    league_id        INTEGER  NOT NULL,  -- signed: -1 marks unaffiliated teams
    sport_id INTEGER CHECK (sport_id>=0) NOT NULL,
    location_name    TEXT,
    venue_id INTEGER CHECK (venue_id>=0),
    spring_league_id INTEGER CHECK (spring_league_id>=0),
    spring_venue_id INTEGER CHECK (spring_venue_id>=0),
    parent_org_id INTEGER CHECK (parent_org_id>=0),
    -----------------------------------------------------------
    CONSTRAINT pk_team_seasons PRIMARY KEY (team_id, season_id)
);

--rollback;
commit;