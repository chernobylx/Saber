import polars as pl
import dataframely as dy
from dataframely.exc import ValidationError
from dataframely.filter_result import FilterResult, LazyFilterResult

link_regex = r'/api/v\d(?:\.\d)?((?:/[a-zA-Z0-9]+)+)'
class SportSchema(dy.Schema):
    sport_id = dy.UInt32(nullable=False, primary_key=True)
    sport_code = dy.String(nullable=False, unique=True, max_length=3)
    sport_name = dy.String(nullable=False, unique=True)
    sport_abbr = dy.String(nullable=False, unique=True)
    sort_order = dy.UInt32(nullable=False, unique=True)
    sport_link = dy.String(nullable=False, unique=True, regex=link_regex)

class LeagueSchema(dy.Schema):
    league_id = dy.UInt32(nullable=False, primary_key=True)
    sport_id = dy.UInt32(nullable=False,primary_key=True)
    league_name = dy.String(nullable=False, unique=False)
    league_abbr = dy.String(nullable=False, unique=True)
    last_season = dy.UInt32(nullable=False)
    is_active = dy.Bool(nullable=False)
    sort_order = dy.UInt32(nullable=False, unique=True)
    league_link = dy.String(nullable=False, unique=True, regex=link_regex)

class SeasonSchema(dy.Schema):
    league_id = dy.UInt32(nullable=False, primary_key=True)
    season = dy.UInt32(nullable=False, primary_key=True)
    n_games = dy.UInt32(nullable=False)
    n_teams = dy.UInt32(nullable=False)
    has_divisions = dy.Bool(nullable=False)
    n_wildcard_teams = dy.UInt32(nullable=False)
    pre_season_start = dy.Date(nullable=False)
    pre_season_end = dy.Date(nullable=False)
    season_start = dy.Date(nullable=False)
    season_end = dy.Date(nullable=False)
    spring_start = dy.Date(nullable=True)
    spring_end = dy.Date(nullable=True)
    regular_start = dy.Date(nullable=False)
    first_half_end = dy.Date(nullable=True)
    all_star_game = dy.Date(nullable=True)
    second_half_start = dy.Date(nullable=True)
    regular_end = dy.Date(nullable=False)
    post_start = dy.Date(nullable=True)
    post_end = dy.Date(nullable=True)
    off_start = dy.Date(nullable=False)
    off_end = dy.Date(nullable=False)

    @dy.rule()
    def general_causality(cls)->pl.Expr:
        expr = pl.col('pre_season_start') < pl.col('pre_season_end')
        expr &= pl.col('pre_season_end') <= pl.col('season_start')
        expr &= pl.col('season_start') < pl.col('season_end')
        expr &= pl.col('season_start') <= pl.col('regular_start')
        expr &= pl.col('regular_start') < pl.col('regular_end')
        expr &= pl.col('regular_end') <= pl.col('season_end')
        expr &= pl.col('season_end') <= pl.col('off_start')
        expr &= pl.col('off_start') < pl.col('off_end')
        return expr

    @dy.rule()
    def all_star_causality(cls):
        expr = pl.col('first_half_end') < pl.col('all_star_game') < pl.col('second_half_start')
        expr |= (
                    (pl.col('all_star_game').is_null() &
                    (pl.col('first_half_start') < pl.col('second_half_start')))
                )
        expr |= pl.all_horizontal(
                    pl.col('all_star_game').is_null(),
                    pl.col('first_half_start').is_null(),
                    pl.col('second_half_start').is_null()
                )
        return expr

class SportCollection(dy.Collection):
    sports: dy.LazyFrame[SportSchema]
    leagues: dy.LazyFrame[LeagueSchema]

    @dy.filter()
    def leagues_foreign_key(self)->pl.LazyFrame:
        return self.sports.select('sport_id')





def transform_sports(df: pl.LazyFrame) -> pl.LazyFrame:
    #rename columns to match schema
    df = df.select(
 pl.col('id').alias('sport_id'),
        pl.col('code').alias('sport_code'),
        pl.col('name').alias('sport_name'),
        pl.col('abbreviation').alias('sport_abbr'),
        pl.col('sortOrder').alias('sort_order'),
        pl.col('link').alias('sport_link')
    )

    return df

def transform_leagues(df: pl.LazyFrame)-> pl.LazyFrame:
    df = df.with_columns(
        pl.when(
            ~pl.col('abbreviation').is_unique() & pl.col('season').ne('2026')
        ).then(
            pl.col('abbreviation')+' ('+pl.col('season')+')'
        ).otherwise(
            pl.col('abbreviation')
        ),

        pl.when(
            pl.col('sport.id').is_null() & pl.col('active')
        ).then(
            1
        ).otherwise(
            pl.col('sport.id')
        ).alias('sport.id')
    ).filter(
        ~pl.col('sport.id').is_null()
    ).with_columns(
        pl.when(
            pl.col('name').str.contains('CONCEBE')
        ).then(
            pl.col('sortOrder')+1
        ).otherwise(
            pl.col('sortOrder')
        )
    ).select(
        pl.col('id').alias('league_id'),
        pl.col('sport.id').alias('sport_id'),
        pl.col('name').alias('league_name'),
        pl.col('abbreviation').alias('league_abbr'),
        pl.col('season').alias('last_season'),
        pl.col('active').alias('is_active'),
        pl.col('sortOrder').alias('sort_order'),
        pl.col('link').alias('league_link')
    )

    return df






