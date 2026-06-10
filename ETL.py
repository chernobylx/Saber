import marimo

__generated_with = "0.23.9"
app = marimo.App(width="columns")


@app.cell(column=0)
def _():
    import polars as pl
    from extract import endpoints, get
    from transform import (transform_sports, transform_leagues, transform_seasons,
                           transform_divisions, transform_teams,TeamsBySeasonSchema)
    from transform import (DivisionSchema, DivisionSeasonsSchema,SportSchema, LeagueSchema,
                           SeasonSchema, TeamSchema)
    from transform import SportsSeasons, LeagueCollection
    from pathlib import Path
    import duckdb
    import marimo as mo

    db = duckdb.connect("data/statsapi/statsapi.duckdb")
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
        db,
        endpoints,
        get,
        mo,
        pl,
        transform_divisions,
        transform_leagues,
        transform_seasons,
        transform_sports,
        transform_teams,
    )


@app.cell
def _(Path, endpoints, get):
    data = Path('data/statsapi')
    #create folder if necessary
    if not data.exists():
        data.mkdir(parents=True)
    #get list of tables to load
    tables = endpoints.keys()
    #build file paths
    paths = [data/(table+'.parquet') for table in tables]
    #download missing tables
    for table, path in zip(tables, paths, strict=True):
        if not path.exists():
            get(table).collect().write_parquet(path)
    return (data,)


@app.cell
def _(
    DivisionSchema,
    DivisionSeasonsSchema,
    LeagueCollection,
    LeagueSchema,
    SeasonSchema,
    SportSchema,
    SportsSeasons,
    TeamSchema,
    TeamsBySeasonSchema,
    data,
    pl,
    transform_divisions,
    transform_leagues,
    transform_seasons,
    transform_sports,
    transform_teams,
):
    #scan disk
    sports = pl.scan_parquet(data/'sports.parquet')
    leagues = pl.scan_parquet(data/'leagues.parquet')
    divisions = pl.scan_parquet(data/'divisions.parquet')
    seasons = pl.scan_parquet(data/'seasons.parquet')
    teams = pl.scan_parquet(data/'teams.parquet')
    #apply schemas
    sports = transform_sports(sports)
    leagues = transform_leagues(leagues)
    divisions, division_seasons = transform_divisions(divisions, leagues)
    seasons = transform_seasons(seasons)
    teams, team_seasons = transform_teams(teams)
    #validate schemas
    sports = SportSchema.validate(sports, cast=True).lazy()
    leagues =  LeagueSchema.validate(leagues, cast=True).lazy()
    seasons = SeasonSchema.validate(seasons, cast=True).lazy()
    divisions = DivisionSchema.validate(divisions, cast=True).lazy()
    division_seasons = DivisionSeasonsSchema.validate(division_seasons, cast=True).lazy()
    teams = TeamSchema.validate(teams, cast=True).lazy()
    team_seasons = team_seasons.with_columns(
        pl.col.league_id.fill_null(-1)
    )
    team_seasons = TeamsBySeasonSchema.validate(team_seasons, cast=True).lazy()

    SC, bad = SportsSeasons.filter({'sports':sports, 'seasons':seasons})
    LC = LeagueCollection.validate({
        'leagues': leagues,
        'divisions': divisions,
        'seasons': SC.seasons,
        'team_seasons': team_seasons
    })
    return


@app.cell
def _(Path, db):
    #create tables from the versioned schema (see sql/schema.sql)
    db.execute(Path('sql/schema.sql').read_text())
    db.sql("SHOW ALL TABLES")
    return


@app.cell
def _(SeasonSchema):
    SeasonSchema
    return


@app.cell(column=1)
def _():
    return


if __name__ == "__main__":
    app.run()
