"""Tests for the transform_* functions and their dataframely schemas.

Each transform is checked two ways: (1) its output validates against the
corresponding schema, and (2) the specific normalization logic behaves as
intended. We test the logic, not the live API data."""

import datetime

import polars as pl

from tests.conftest import collect, season_row
from transform import (
    DivisionSchema,
    DivisionSeasonsSchema,
    LeagueSchema,
    SeasonSchema,
    SportSchema,
    TeamsBySeasonSchema,
    TeamSchema,
    transform_divisions,
    transform_leagues,
    transform_seasons,
    transform_sports,
    transform_teams,
)


def test_transform_sports_validates(raw_sports):
    out = SportSchema.validate(transform_sports(raw_sports), cast=True)
    df = out.lazy().collect()
    assert set(df["sport_id"]) == {1, 99}
    assert df.filter(pl.col("sport_id") == 1)["sport_code"][0] == "mlb"


def test_transform_leagues_validates(raw_leagues):
    out = LeagueSchema.validate(transform_leagues(raw_leagues), cast=True)
    df = out.lazy().collect()
    assert set(df["league_id"]) == {103, 104}
    assert df["last_season"].dtype == pl.UInt32  # cast from the string "2024"


def test_transform_leagues_disambiguates_duplicate_abbr():
    # two leagues share abbreviation "FL" in non-current seasons -> the season
    # is appended to keep league_abbr unique
    raw = pl.LazyFrame(
        [
            {"id": 1, "name": "Federal League", "abbreviation": "FL",
             "season": "1914", "active": False, "sortOrder": 1,
             "link": "/api/v1/league/1"},
            {"id": 2, "name": "Florida League", "abbreviation": "FL",
             "season": "1915", "active": False, "sortOrder": 2,
             "link": "/api/v1/league/2"},
        ]
    )
    df = collect(transform_leagues(raw))
    abbrs = set(df["league_abbr"])
    assert abbrs == {"FL (1914)", "FL (1915)"}


def test_transform_seasons_validates(raw_seasons):
    out = SeasonSchema.validate(transform_seasons(raw_seasons), cast=True)
    df = out.lazy().collect()
    assert df.height == 1
    assert df["league_id"][0] == 103


def test_transform_seasons_fills_null_pre_end_from_season_start():
    raw = pl.LazyFrame(
        [season_row({"seasonDateInfo.preSeasonEndDate": None})]
    )
    df = collect(transform_seasons(raw))
    assert df["pre_end"][0] == df["season_start"][0]


def test_transform_seasons_fills_null_off_start_from_season_end():
    raw = pl.LazyFrame(
        [season_row({"seasonDateInfo.offseasonStartDate": None})]
    )
    df = collect(transform_seasons(raw))
    assert df["off_start"][0] == df["season_end"][0] + datetime.timedelta(days=1)


def test_transform_seasons_clamps_regular_end_to_season_end():
    # regular season "ends" after the season itself -> clamp to season_end
    raw = pl.LazyFrame(
        [
            season_row(
                {
                    "seasonDateInfo.regularSeasonEndDate": "2024-12-15",
                    "seasonDateInfo.seasonEndDate": "2024-11-01",
                }
            )
        ]
    )
    df = collect(transform_seasons(raw))
    assert df["regular_end"][0] == df["season_end"][0]


def test_transform_seasons_drops_rows_missing_game_counts():
    raw = pl.LazyFrame(
        [season_row({"numGames": None}), season_row({"id": 104})]
    )
    df = collect(transform_seasons(raw))
    assert df.height == 1
    assert df["league_id"][0] == 104


def test_transform_divisions_validates(raw_divisions, raw_leagues):
    leagues = transform_leagues(raw_leagues)
    divisions, division_seasons = transform_divisions(raw_divisions, leagues)
    div_df = DivisionSchema.validate(divisions, cast=True).lazy().collect()
    ds_df = DivisionSeasonsSchema.validate(
        division_seasons, cast=True
    ).lazy().collect()
    assert set(div_df["division_id"]) == {200, 201}
    assert ds_df.height == 2  # one (division, season) row per division


def test_transform_divisions_backfills_null_name_from_league(
    raw_divisions, raw_leagues
):
    leagues = transform_leagues(raw_leagues)
    divisions, _ = transform_divisions(raw_divisions, leagues)
    df = collect(divisions)
    name_201 = df.filter(pl.col("division_id") == 201)["division_name"][0]
    assert name_201 == "American League(201)"


def test_transform_teams_validates(raw_teams):
    teams, team_seasons = transform_teams(raw_teams)
    teams_df = TeamSchema.validate(teams, cast=True).lazy().collect()
    # team_seasons needs the -1 sentinel applied, as ETL.py does, before validate
    team_seasons = team_seasons.with_columns(pl.col("league_id").fill_null(-1))
    ts_df = TeamsBySeasonSchema.validate(
        team_seasons, cast=True
    ).lazy().collect()
    assert set(teams_df["team_id"]) == {147, 119}
    assert teams_df.height == 2  # one row per team despite multiple seasons
    assert ts_df.filter(pl.col("team_id") == 119)["league_id"][0] == -1


def test_transform_teams_backfills_location_from_mode(raw_teams):
    _, team_seasons = transform_teams(raw_teams)
    df = collect(team_seasons)
    loc_2024 = df.filter(
        (pl.col("team_id") == 147) & (pl.col("season") == 2024)
    )["location_name"][0]
    assert loc_2024 == "New York"  # backfilled from the 2023 row
