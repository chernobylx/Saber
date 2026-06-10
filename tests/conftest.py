"""Shared fixtures: small synthetic raw frames in the json-normalized shape
the transform_* functions expect (column names like 'sport.id',
'seasonDateInfo.preSeasonStartDate'). No network or cached data is touched."""

import polars as pl
import pytest


def collect(lf: pl.LazyFrame) -> pl.DataFrame:
    """Collect a LazyFrame to an eager DataFrame.

    Wrapper exists so call sites get a precise `pl.DataFrame` type: ty does not
    currently narrow polars' overloaded `LazyFrame.collect()` return type and
    otherwise infers `InProcessQuery | DataFrame`."""
    return lf.collect()  # ty: ignore[invalid-return-type]


def season_row(overrides: dict | None = None) -> dict:
    """A single valid raw season record. Pass `overrides` to mutate fields
    for a specific test (keys use the json-normalized dotted names)."""
    row = {
        "id": 103,
        "season": 2024,
        "sport.id": 1,
        "numGames": 162,
        "numTeams": 15,
        "divisionsInUse": True,
        "hasSplitSeason": False,
        "numWildcardTeams": 3,
        "seasonDateInfo.preSeasonStartDate": "2024-02-01",
        "seasonDateInfo.preSeasonEndDate": "2024-02-20",
        "seasonDateInfo.seasonStartDate": "2024-02-21",
        "seasonDateInfo.springStartDate": "2024-02-22",
        "seasonDateInfo.springEndDate": "2024-03-25",
        "seasonDateInfo.regularSeasonStartDate": "2024-03-28",
        "seasonDateInfo.lastDate1stHalf": "2024-07-14",
        "seasonDateInfo.allStarDate": "2024-07-16",
        "seasonDateInfo.firstDate2ndHalf": "2024-07-19",
        "seasonDateInfo.regularSeasonEndDate": "2024-09-29",
        "seasonDateInfo.postSeasonStartDate": "2024-10-01",
        "seasonDateInfo.postSeasonEndDate": "2024-10-31",
        "seasonDateInfo.seasonEndDate": "2024-11-01",
        "seasonDateInfo.offseasonStartDate": "2024-11-02",
        "seasonDateInfo.offSeasonEndDate": "2025-01-31",
    }
    if overrides:
        row.update(overrides)
    return row


@pytest.fixture
def raw_sports() -> pl.LazyFrame:
    # sport_id 99 has no season (used to exercise the SportsSeasons filter)
    return pl.LazyFrame(
        [
            {"id": 1, "code": "mlb", "name": "Major League Baseball",
             "abbreviation": "MLB", "sortOrder": 11, "link": "/api/v1/sports/1"},
            {"id": 99, "code": "win", "name": "Winter Leagues",
             "abbreviation": "WIN", "sortOrder": 12, "link": "/api/v1/sports/99"},
        ]
    )


@pytest.fixture
def raw_leagues() -> pl.LazyFrame:
    return pl.LazyFrame(
        [
            {"id": 103, "name": "American League", "abbreviation": "AL",
             "season": "2024", "active": True, "sortOrder": 21,
             "link": "/api/v1/league/103"},
            {"id": 104, "name": "National League", "abbreviation": "NL",
             "season": "2024", "active": True, "sortOrder": 22,
             "link": "/api/v1/league/104"},
        ]
    )


@pytest.fixture
def raw_seasons() -> pl.LazyFrame:
    return pl.LazyFrame([season_row()])


@pytest.fixture
def raw_divisions() -> pl.LazyFrame:
    # id 201 has a null name -> should be backfilled from the league name + id
    return pl.LazyFrame(
        [
            {"id": 200, "name": "AL East", "season": 2024, "league.id": 103,
             "active": True, "link": "/api/v1/divisions/200", "sport.id": 1},
            {"id": 201, "name": None, "season": 2024, "league.id": 103,
             "active": True, "link": "/api/v1/divisions/201", "sport.id": 1},
        ]
    )


def _team_row(overrides: dict | None = None) -> dict:
    row = {
        "id": 147, "season": 2024, "name": "New York Yankees",
        "teamCode": "nya", "locationName": "New York", "league.id": 103,
        "sport.id": 1, "division.id": 200, "venue.id": 3313,
        "springLeague.id": 114, "springVenue.id": 2523,
        "link": "/api/v1/teams/147", "active": True, "parentOrgId": None,
    }
    if overrides:
        row.update(overrides)
    return row


@pytest.fixture
def raw_teams() -> pl.LazyFrame:
    return pl.LazyFrame(
        [
            # same team across two seasons; 2024 location is null -> backfilled
            _team_row({"season": 2023, "locationName": "New York"}),
            _team_row({"season": 2024, "locationName": None}),
            # unaffiliated team: league.id is null -> becomes -1 downstream
            _team_row(
                {
                    "id": 119, "season": 2024, "name": "Los Angeles Dodgers",
                    "teamCode": "lad", "locationName": "Los Angeles",
                    "league.id": None, "division.id": None, "venue.id": 22,
                    "springLeague.id": None, "springVenue.id": None,
                    "link": "/api/v1/teams/119",
                }
            ),
        ]
    )
