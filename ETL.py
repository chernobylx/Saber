import marimo

__generated_with = "0.23.9"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import polars as pl

    from extract import endpoints, get
    from transform import (
        DivisionSchema,
        DivisionSeasonsSchema,
        LeagueCollection,
        LeagueSchema,
        LeagueSeasonSchema,
        SportSchema,
        SportsCollection,
        TeamSeasonSchema,
        TeamSchema,
        transform_divisions,
        transform_leagues,
        transform_seasons,
        transform_sports,
        transform_teams,
    )

    import sqlalchemy


    return (
        DivisionSchema,
        DivisionSeasonsSchema,
        LeagueCollection,
        LeagueSchema,
        LeagueSeasonSchema,
        Path,
        SportSchema,
        SportsCollection,
        TeamSchema,
        TeamSeasonSchema,
        endpoints,
        get,
        pl,
        sqlalchemy,
        transform_divisions,
        transform_leagues,
        transform_seasons,
        transform_sports,
        transform_teams,
    )


@app.cell
def _(sqlalchemy):
    DATABASE_URL = f"postgresql://postgres:POSTGRES_PASSWORD@localhost:5432/saber"
    engine = sqlalchemy.create_engine(DATABASE_URL)
    return (engine,)


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
    LeagueSeasonSchema,
    SportSchema,
    SportsCollection,
    TeamSchema,
    TeamSeasonSchema,
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
    league_seasons = transform_seasons(seasons)
    league_seasons = LeagueSeasonSchema.validate(league_seasons, cast=True).lazy()
    teams, team_seasons = transform_teams(teams, league_seasons)
    #validate schemas
    sports = SportSchema.validate(sports, cast=True).lazy()
    leagues =  LeagueSchema.validate(leagues, cast=True).lazy()
    #league_seasons = LeagueSeasonSchema.validate(league_seasons, cast=True).lazy()
    divisions = DivisionSchema.validate(divisions, cast=True).lazy()
    division_seasons = DivisionSeasonsSchema.validate(
        division_seasons, cast=True
    ).lazy()
    teams = TeamSchema.validate(teams, cast=True).lazy()
    team_seasons = team_seasons.with_columns(
        pl.col.league_id.fill_null(-1)
    )
    team_seasons = TeamSeasonSchema.validate(team_seasons, cast=True).lazy()

    SC, bad = SportsCollection.filter({'sports':sports, 'league_seasons':league_seasons, 'team_seasons': team_seasons})
    LC = LeagueCollection.validate({
        'leagues': leagues,
        'divisions': divisions,
        'league_seasons': SC.league_seasons,
        'team_seasons': team_seasons
    })
    return LC, SC, teams


@app.cell
def _(LC, SC, engine, teams):
    frames = {
        'api.sports': SC.sports,
        'api.leagues': LC.leagues,
        'api.teams': teams,
        'api.league_seasons': LC.league_seasons,
        'api.divisions': LC.divisions,
        'api.team_seasons': LC.team_seasons,
    }
    for _table, _lf in frames.items():
        _lf.collect().write_database(
            table_name=_table,
            connection=engine,
            engine='sqlalchemy',
            if_table_exists='append',
        )
    return


if __name__ == "__main__":
    app.run()
