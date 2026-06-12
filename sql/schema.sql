-- Schema for data/statsapi/statsapi.duckdb
--
-- Tables mirror the dataframely schemas in transform.py (column names,
-- nullability, and keys). The parquet files under data/statsapi/ are an
--
-- link columns share the same shape; the regex is repeated per table because
rollback;

Begin Transaction;

drop schema if exists api cascade;

CREATE SCHEMA api;


CREATE DOMAIN api.API_LINK as TEXT
    CHECK (VALUE ~ '/api/v\d(?:\.\d)?((?:/[a-zA-Z0-9]+)+)');

create type api.roster_status as
	enum ('A','RM','D10','D15','CL','RL','MIN','D60','TR','NRI','DES','FA','RT','WA','ASG');

create type api.positions as
	enum ('1','2','3','4','5','6','7','8','9','10','11','12','I','O','Y');

create type api.gender as enum ('M','F','NB');
create type api.chirality as  enum ('L','R','S');


CREATE TABLE api.sports (
    sport_id    INTEGER CHECK (sport_id>=0),
    sport_code  TEXT     UNIQUE NOT NULL,
    sport_name  TEXT     UNIQUE NOT NULL,
    sport_abbr TEXT     UNIQUE NOT NULL,
    sort_order INTEGER CHECK (sort_order>=0) UNIQUE NOT NULL,
    sport_link API_LINK     UNIQUE NOT NULL,
    --------------------------------------------
    CONSTRAINT pk_sports PRIMARY KEY (sport_id)
);

CREATE TABLE api.leagues (
    league_id INTEGER CHECK (league_id>=0),
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
    team_id INTEGER CHECK (team_id>=0),
    team_link API_LINK     UNIQUE NOT NULL,
    is_active BOOLEAN  NOT NULL,
    first_year integer check (first_year>0),
    -------------------------------------------------------------
    CONSTRAINT pk_teams PRIMARY KEY (team_id)
);


CREATE TABLE api.league_seasons (
    season_id INTEGER,
    league_id INTEGER NOT null, 
    year INTEGER CHECK (year>=0) NOT NULL,
    sport_id INTEGER not null,
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
    constraint pk_seasons primary key (season_id),
    CONSTRAINT unique_year_league  UNIQUE (year, league_id),
    constraint fk_league_seasons_leagues foreign key (league_id) REFERENCES api.leagues (league_id),
    constraint fk_league_seasons_sports foreign key (sport_id) REFERENCES api.sports (sport_id)
);

CREATE TABLE api.divisions (
    division_id INTEGER CHECK (division_id>=0),
    division_name TEXT     UNIQUE NOT NULL,
    league_id INTEGER  NOT NULL ,
    is_active     BOOLEAN  NOT NULL,
    division_link API_LINK     UNIQUE NOT null,
    --------------------------------------------------------------
    constraint pk_divisions primary key (division_id),
    constraint fk_divisions_leagues foreign key (league_id) REFERENCES api.leagues (league_id)
    
);


CREATE TABLE api.team_seasons (
	squad_id INTEGER not null,
    team_id INTEGER NOT NULL ,
    league_id        INTEGER  ,  -- signed: -1 marks unaffiliated teams
    year INTEGER NOT NULL,
    sport_id INTEGER not null,
    division_id INTEGER,
    team_name        TEXT     NOT NULL,
    team_code        TEXT     NOT NULL,
    location_name    TEXT,
    venue_id INTEGER CHECK (venue_id>=0),
    spring_league_id INTEGER CHECK (spring_league_id>=0),
    spring_venue_id INTEGER CHECK (spring_venue_id>=0),
    parent_org_id INTEGER references api.teams (team_id),
    -----------------------------------------------------------
    CONSTRAINT pk_team_seasons primary key(squad_id),
    constraint fk_team_seasons_leagues foreign key (league_id) references api.leagues (league_id),
    constraint fk_team_seasons_teams foreign key (team_id) REFERENCES api.teams (team_id),
    constraint fk_team_seasons_league_seasons foreign key (league_id, year) REFERENCES api.league_seasons (league_id, year),
    constraint fk_team_seasons_divisions foreign key (division_id) references api.divisions  (division_id),
    constraint fk_team_seasons_spring_league foreign key (spring_league_id) references api.leagues (league_id),
    constraint fk_team_seasons_sports foreign key (sport_id) references api.sports (sport_id)
);

create type api.roster_types
	as enum ('active', 'gameday', '40Man', 'full_season', 'depth_chart','coach','all_time', 'full_roster', 'non_roster_invitee');


create table api.rosters(
	roster_id integer not null,
	squad_id integer,
	roster_type ROSTER_TYPES,
	------------------------------------------------------------------
	constraint pk_rosters primary key (roster_id),
	constraint fk_rosters_team_seasons foreign key (squad_id) references api.team_seasons  (squad_id)
);


create table api.roster_players (
	roster_id integer not null,
	player_id integer not null,
	player_status roster_status not null,
	jersey_num integer check(jersey_num>0),
	player_position positions not null,
	note varchar(255),
	-----------------------------------------------
	constraint fk_roster_id foreign key (roster_id) references  api.rosters (roster_id)
);

create table api.players(
	player_id integer unique not null primary key check (player_id >0),
	first_name varchar(255) not null,
	middle_name varchar(255),
	last_name varchar(255) not null,
	birth_city varchar(255) not null,
	birth_date date not null,
	birth_state_province varchar(255),
	height_inches integer not null,
	weight_lb integer not null,
	boxscore_name varchar(255),
	gender gender,
	draft_year integer check (draft_year >1870),
	mlb_debut date,
	last_played_date date,
	sz_top float not null check (sz_top >0),
	primary_pos positions not null,
	bat_side chirality not null,
	pitch_hand chirality not null,
	pronounciation varchar(255),
	player_link api_link not null 
	
);

alter table api.roster_players
	add constraint fk_roster_players_players foreign key (player_id) references api.players (player_id);
commit;