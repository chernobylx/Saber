"""Tests for the dataframely Collections (cross-table integrity rules)."""

import polars as pl

from transform import (
    LeagueCollection,
    LeagueSchema,
    SeasonSchema,
    SportSchema,
    SportsSeasons,
    TeamsBySeasonSchema,
    transform_leagues,
    transform_seasons,
    transform_sports,
    transform_teams,
)


def _validated_seasons(raw_seasons):
    return SeasonSchema.validate(transform_seasons(raw_seasons), cast=True).lazy()


def test_sports_seasons_drops_sport_without_season(raw_sports, raw_seasons):
    # raw_sports has sport_id 1 and 99; raw_seasons only references sport_id 1
    sports = SportSchema.validate(transform_sports(raw_sports), cast=True).lazy()
    seasons = _validated_seasons(raw_seasons)
    valid, _failures = SportsSeasons.filter({"sports": sports, "seasons": seasons})
    kept = set(valid.sports.collect()["sport_id"])
    assert kept == {1}  # 99 dropped: no season references it


def _league_collection_inputs(raw_leagues, raw_teams, raw_seasons):
    leagues = LeagueSchema.validate(
        transform_leagues(raw_leagues), cast=True
    ).lazy()
    _teams, team_seasons = transform_teams(raw_teams)
    team_seasons = team_seasons.with_columns(pl.col("league_id").fill_null(-1))
    team_seasons = TeamsBySeasonSchema.validate(
        team_seasons, cast=True
    ).lazy()
    # divisions can be empty for this collection's foreign-key check
    divisions = pl.LazyFrame(
        schema={
            "division_id": pl.UInt32, "division_name": pl.String,
            "league_id": pl.UInt32, "is_active": pl.Boolean,
            "division_link": pl.String,
        }
    )
    return {
        "leagues": leagues,
        "divisions": divisions,
        "seasons": _validated_seasons(raw_seasons),
        "team_seasons": team_seasons,
    }


def test_league_collection_keeps_unaffiliated_team(
    raw_leagues, raw_teams, raw_seasons
):
    inputs = _league_collection_inputs(raw_leagues, raw_teams, raw_seasons)
    lc = LeagueCollection.validate(inputs)
    ts = lc.team_seasons.collect()
    # the -1 (unaffiliated) team survives the foreign-key filter
    assert -1 in set(ts["league_id"])
    assert 119 in set(ts["team_id"])


def test_league_collection_drops_invalid_league_id(
    raw_leagues, raw_teams, raw_seasons
):
    inputs = _league_collection_inputs(raw_leagues, raw_teams, raw_seasons)
    # inject a team referencing a league that does not exist
    bogus = inputs["team_seasons"].collect().with_columns(
        pl.when(pl.col("team_id") == 147)
        .then(pl.lit(999))
        .otherwise(pl.col("league_id"))
        .alias("league_id")
    )
    inputs["team_seasons"] = bogus.lazy()
    valid, _failures = LeagueCollection.filter(inputs)
    ts = valid.team_seasons.collect()
    assert 999 not in set(ts["league_id"])
