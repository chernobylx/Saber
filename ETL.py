import marimo

__generated_with = "0.23.9"
app = marimo.App(width="columns")


@app.cell(column=0)
def _():
    from pathlib import Path

    import duckdb
    import marimo as mo
    import polars as pl

    from extract import endpoints, get
    from transform import (
        DivisionSchema,
        DivisionSeasonsSchema,
        LeagueCollection,
        LeagueSchema,
        SeasonSchema,
        SportSchema,
        SportsSeasons,
        TeamsBySeasonSchema,
        TeamSchema,
        transform_divisions,
        transform_leagues,
        transform_seasons,
        transform_sports,
        transform_teams,
    )



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
        duckdb,
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
    division_seasons = DivisionSeasonsSchema.validate(
        division_seasons, cast=True
    ).lazy()
    teams = TeamSchema.validate(teams, cast=True).lazy()
    team_seasons = team_seasons.with_columns(
        pl.col.league_id.fill_null(-1)
    )
    team_seasons = TeamsBySeasonSchema.validate(team_seasons, cast=True).lazy()

    SC, _bad = SportsSeasons.filter({'sports':sports, 'seasons':seasons})
    LC = LeagueCollection.validate({
        'leagues': leagues,
        'divisions': divisions,
        'seasons': SC.seasons,
        'team_seasons': team_seasons
    })
    return


@app.cell
def _(Path, duckdb):
    #(re)create the tables, then load the validated, integrity-checked frames.
    #CREATE OR REPLACE in schema.sql makes this idempotent across reruns.
    with duckdb.connect("data/statsapi/statsapi.duckdb") as db:
        db.execute(Path('sql/schema.sql').read_text())

    return (db,)


app._unparsable_cell(
    r"""
    frames = {
        'sports': SC.sports,
        'leagues': LC.leagues,
        'seasons': LC.seasons,
        'divisions': LC.divisions,
        'division_seasons': division_seasons,
        'teams': teams,
        'team_seasons': LC.team_seasons,
    }
    with db = duckdb.connect("data/statsapi/statsapi.duckdb"):
        for _name, _lf in frames.items():
            _frame = _lf.collect()
            db.register('_load', _frame)
            db.execute(f"INSERT INTO main.{_name} BY NAME SELECT * FROM _load")
            db.unregister('_load')

        db.sql("SHOW ALL TABLES")
    """,
    name="_"
)


@app.cell
def _():
    import sqlalchemy

    DATABASE_URL = f"postgresql://postgres:POSTGRES_PASSWORD@localhost:5432/postgres"
    engine = sqlalchemy.create_engine(DATABASE_URL)
    return (engine,)


@app.cell(hide_code=True)
def _(engine, mo):
    _df = mo.sql(
        f"""
        SHOW ALL TABLES
        """,
        engine=engine
    )
    return


@app.cell
def _(db):
    db.close()
    return


@app.cell(column=1)
def _():
    return


if __name__ == "__main__":
    app.run()
