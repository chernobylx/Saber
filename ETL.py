import marimo

__generated_with = "0.23.9"
app = marimo.App()


@app.cell
def _():
    import polars as pl
    from extract import endpoints, get
    from transform import (transform_sports, transform_leagues, transform_seasons,                   transform_divisions, transform_teams,TeamsBySeasonSchema)
    import altair as alt
    alt.data_transformers.enable("vegafusion")
    from transform import (DivisionSchema, DivisionSeasonsSchema,SportSchema, LeagueSchema,
                           SeasonSchema, TeamSchema)
    from transform import SportsSeasons, LeagueCollection
    from pathlib import Path

    import marimo as mo

    return (
        DivisionSchema,
        DivisionSeasonsSchema,
        LeagueCollection,
        LeagueSchema,
        Path,
        SeasonSchema,
        SportSchema,
        SportsSeasons,
        TeamSchema,
        TeamsBySeasonSchema,
        endpoints,
        get,
        pl,
        transform_divisions,
        transform_leagues,
        transform_seasons,
        transform_sports,
        transform_teams,
    )


@app.cell
def _(Path, endpoints):
    data = Path('data/statsapi')
    tables = endpoints.keys()
    paths = [data/(table+'.parquet') for table in tables]
    return data, paths, tables


@app.cell
def _(get, paths, tables):
    for table, path in zip(tables, paths):
        if not path.exists():
            get(table).collect().write_parquet(path)
    return


@app.cell
def _(data, pl):
    sports = pl.scan_parquet(data/'sports.parquet')
    leagues = pl.scan_parquet(data/'leagues.parquet')
    divisions = pl.scan_parquet(data/'divisions.parquet')
    seasons = pl.scan_parquet(data/'seasons.parquet')
    teams = pl.scan_parquet(data/'teams.parquet')
    return divisions, leagues, seasons, sports, teams


@app.cell
def _(SportSchema, sports, transform_sports):
    sports_1 = transform_sports(sports)
    sports_1 = SportSchema.validate(sports_1, cast=True).lazy()
    return (sports_1,)


@app.cell
def _(LeagueSchema, leagues, transform_leagues):
    leagues_1 = transform_leagues(leagues)
    leagues_1 = LeagueSchema.validate(leagues_1, cast=True).lazy()
    return (leagues_1,)


@app.cell
def _(SeasonSchema, seasons, transform_seasons):
    seasons_1 = transform_seasons(seasons)
    seasons_1 = SeasonSchema.validate(seasons_1, cast=True).lazy()
    return (seasons_1,)


@app.cell
def _(SportsSeasons, seasons_1, sports_1):
    SC, bad = SportsSeasons.filter({'sports': sports_1, 'seasons': seasons_1})
    return SC, bad


@app.cell
def _(bad):
    bad['sports']._df
    return


@app.cell
def _(
    DivisionSchema,
    DivisionSeasonsSchema,
    divisions,
    leagues_1,
    transform_divisions,
):
    div, div_seasons = transform_divisions(divisions, leagues_1)
    divisions_1 = DivisionSchema.validate(div, cast=True).lazy()
    division_seasons = DivisionSeasonsSchema.validate(div_seasons, cast=True).lazy()
    return (divisions_1,)


@app.cell
def _(TeamSchema, TeamsBySeasonSchema, pl, teams, transform_teams):
    teams_1, team_seasons = transform_teams(teams)
    teams_1 = TeamSchema.validate(teams_1, cast=True).lazy()
    team_seasons = team_seasons.with_columns(
        pl.col.league_id.fill_null(0)
    )
    team_seasons = TeamsBySeasonSchema.validate(team_seasons, cast=True).lazy()
    return (team_seasons,)


@app.cell
def _(LeagueCollection, SC, divisions_1, leagues_1, team_seasons):
    LC = LeagueCollection.validate({'leagues': leagues_1, 'divisions': divisions_1, 'seasons': SC.seasons, 'team_seasons': team_seasons})
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
