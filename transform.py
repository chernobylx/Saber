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
    is_active = dy.Bool(nullable=False)
    sort_order = dy.UInt32(nullable=False, unique=True)
    league_link = dy.String(nullable=False, unique=True, regex=link_regex)


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
        pl.col('active').alias('is_active'),
        pl.col('sortOrder').alias('sort_order'),
        pl.col('link').alias('league_link')
    )

    return df






