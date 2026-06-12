import dataframely as dy
import polars as pl
from polars import selectors as cs

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
    #sport_id = dy.UInt32(nullable=False,primary_key=True)
    league_name = dy.String(nullable=False, unique=False)
    league_abbr = dy.String(nullable=False, unique=True)
    last_season = dy.UInt32(nullable=False)
    is_active = dy.Bool(nullable=False)
    sort_order = dy.UInt32(nullable=False, unique=True)
    league_link = dy.String(nullable=False, unique=True, regex=link_regex)



class LeagueSeasonSchema(dy.Schema):
    season_id = dy.UInt32(nullable=False, primary_key=True)
    league_id = dy.UInt32(nullable=False, primary_key=True)
    sport_id = dy.UInt32(nullable=False, primary_key=True)
    year = dy.UInt32(nullable=False)
    n_games = dy.UInt32(nullable=False)
    n_teams = dy.UInt32(nullable=False)
    has_divisions = dy.Bool(nullable=False)
    has_split_season = dy.Bool(nullable=False)
    n_wildcard_teams = dy.UInt32(nullable=False)
    pre_start = dy.Date(nullable=False)
    pre_end = dy.Date(nullable=False)
    spring_start = dy.Date(nullable=True)
    spring_end = dy.Date(nullable=True)
    season_start = dy.Date(nullable=False)
    regular_start = dy.Date(nullable=False)
    first_half_end = dy.Date(nullable=True)
    all_star_game = dy.Date(nullable=True)
    second_half_start = dy.Date(nullable=True)
    regular_end = dy.Date(nullable=False)
    post_start = dy.Date(nullable=True)
    post_end = dy.Date(nullable=True)
    season_end = dy.Date(nullable=False)
    off_start = dy.Date(nullable=False)
    off_end = dy.Date(nullable=True)

    @dy.rule()
    def unique_seasons(cls) -> pl.Expr:
        return pl.struct('year', 'league_id').is_unique()
    @dy.rule()
    def general_causality(cls)->pl.Expr:
        expr = pl.col('pre_start') <= pl.col('pre_end')
        expr = expr & (pl.col('pre_end') <= pl.col('season_start'))
        expr = expr & (pl.col('season_start') < pl.col('season_end'))
        expr = expr & (pl.col('season_start') <= pl.col('regular_start'))
        expr = expr & (pl.col('regular_start') < pl.col('regular_end'))
        expr = expr & (pl.col('regular_end') <= pl.col('season_end'))
        #negro league off season starts after regular season end not season end
        expr = expr & (pl.col('regular_end') <= pl.col('off_start'))
        expr &= (pl.col('off_start') < pl.col('off_end')) | pl.col('off_end').is_null()
        expr &= (pl.col('first_half_end')<=pl.col('second_half_start'))
        return expr



class DivisionSchema(dy.Schema):
    division_id = dy.UInt32(nullable=False, primary_key=True)
    division_name = dy.String(nullable=False, unique=True)
    league_id = dy.UInt32(nullable=False, primary_key=True)
    is_active = dy.Bool(nullable=False)
    division_link = dy.String(nullable=False, regex=link_regex, unique=True)

class DivisionSeasonsSchema(dy.Schema):
    division_id = dy.UInt32(nullable=False, primary_key=True)
    season = dy.UInt32(nullable=False, primary_key=True)



    


class TeamSchema(dy.Schema):
    team_id = dy.UInt32(nullable=False, primary_key=True)
    team_link = dy.String(nullable=False, regex=link_regex, unique=True)
    is_active = dy.Bool(nullable=False)
    first_year = dy.UInt32(nullable=True)

class TeamSeasonSchema(dy.Schema):
    squad_id = dy.UInt32(nullable=False, primary_key=True)
    team_id = dy.UInt32(nullable=False)
    league_id = dy.Int32(nullable=False, primary_key=True)
    year = dy.UInt32(nullable=False)
    division_id = dy.UInt32(nullable=True)
    team_name = dy.String(nullable=False)
    team_code = dy.String(nullable=False)
    sport_id = dy.UInt32(nullable=False, primary_key=True)
    location_name = dy.String(nullable=True)
    venue_id = dy.UInt32(nullable=True)
    spring_league_id = dy.UInt32(nullable=True)
    spring_venue_id = dy.UInt32(nullable=True)
    parent_org_id = dy.UInt32(nullable=True)

class SportsCollection(dy.Collection):
    sports: dy.LazyFrame[SportSchema]
    league_seasons: dy.LazyFrame[LeagueSeasonSchema]
    team_seasons: dy.LazyFrame[TeamSeasonSchema]
    
    @dy.filter()
    def league_seasons_sports(self)->pl.LazyFrame:
        #every league season must reference a valid sport and every sport must be referenced by
        # at least one season
        return self.sports.join(
            self.league_seasons,
            on='sport_id',
            how='inner'
        ).select('sport_id').unique().lazy()
    
    @dy.filter()
    def team_seasons_sports(self)->pl.LazyFrame:
        #every team season must reference a valid sport and every sport must be referenced by
        # at least one team_season
        return self.sports.join(
            self.team_seasons,
            on='sport_id',
            how='inner'
        ).select('sport_id').unique().lazy()
    

class LeagueCollection(dy.Collection):
    leagues: dy.LazyFrame[LeagueSchema]
    divisions: dy.LazyFrame[DivisionSchema]
    team_seasons: dy.LazyFrame[TeamSeasonSchema]
    league_seasons: dy.LazyFrame[LeagueSeasonSchema]

    @dy.filter()
    def enforce_foreign_keys(self)->pl.LazyFrame:
        #every reference to league_id must be valid

        #add -1 so that unaffillieated teams are not removed
        
        return pl.concat( [
            self.leagues.select('league_id').cast(pl.Int64),
            pl.LazyFrame(
                {'league_id': [-1]}
            )])

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

        #pl.when(
        #    pl.col('sport.id').is_null() & pl.col('active')
        #).then(
        #    1
        #).otherwise(
        #    pl.col('sport.id')
        #).alias('sport.id')
    #).filter(
    #    ~pl.col('sport.id').is_null()
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
        #pl.col('sport.id').alias('sport_id'),
        pl.col('name').alias('league_name'),
        pl.col('abbreviation').alias('league_abbr'),
        pl.col('season').alias('last_season'),
        pl.col('active').alias('is_active'),
        pl.col('sortOrder').alias('sort_order'),
        pl.col('link').alias('league_link')
    )

    return df

def transform_seasons(lf:pl.LazyFrame)-> pl.LazyFrame:
    lf = lf.select(
        pl.col('id').alias('league_id'),
        pl.col('season').alias('year'),
        pl.col('sport.id').alias('sport_id'),
        pl.col('numGames').alias('n_games'),
        pl.col('numTeams').alias('n_teams'),
        pl.col('divisionsInUse').alias('has_divisions'),
        pl.col('hasSplitSeason').alias('has_split_season'),
        pl.col('numWildcardTeams').alias('n_wildcard_teams'),
        pl.col('seasonDateInfo.preSeasonStartDate').alias('pre_start'),
        pl.col('seasonDateInfo.preSeasonEndDate').alias('pre_end'),
        pl.col('seasonDateInfo.seasonStartDate').alias('season_start'),
        pl.col('seasonDateInfo.springStartDate').alias('spring_start'),
        pl.col('seasonDateInfo.springEndDate').alias('spring_end'),
        pl.col('seasonDateInfo.regularSeasonStartDate').alias('regular_start'),
        pl.col('seasonDateInfo.lastDate1stHalf').alias('first_half_end'),
        pl.col('seasonDateInfo.allStarDate').alias('all_star_game'),
        pl.col('seasonDateInfo.firstDate2ndHalf').alias('second_half_start'),
        pl.col('seasonDateInfo.regularSeasonEndDate').alias('regular_end'),
        pl.col('seasonDateInfo.postSeasonStartDate').alias('post_start'),
        pl.col('seasonDateInfo.postSeasonEndDate').alias('post_end'),
        pl.col('seasonDateInfo.seasonEndDate').alias('season_end'),
        pl.col('seasonDateInfo.offseasonStartDate').alias('off_start'),
        pl.col('seasonDateInfo.offSeasonEndDate').alias('off_end')
    ).with_columns(
        pl.col('n_wildcard_teams').fill_null(0),
        pl.col('has_split_season').fill_null(False),
    ).filter(
        ~pl.col('n_games').is_null() & ~pl.col('n_teams').is_null()
    ).with_columns(
        cs.matches('_(start|end)').cast(pl.datatypes.Date),
        pl.col('all_star_game').cast(pl.datatypes.Date)
    ).with_columns(
        pl.when(
            pl.col('pre_end').is_null()
        ).then(
            pl.col('season_start')
        ).otherwise(
            pl.col('pre_end')
        ).alias('pre_end'),

        pl.when(
            pl.col('off_start').is_null()
        ).then(
            pl.col('season_end') + pl.duration(days=1)
        ).otherwise(
            pl.col('off_start')
        ).alias('off_start')
    ).with_columns(
        pl.when(
            pl.col('regular_end') > pl.col('season_end')
        ).then(
            pl.col('season_end')
        ).otherwise(
            pl.col('regular_end')
        ).alias('regular_end'),

        pl.when(
            pl.col('first_half_end') > pl.col('second_half_start')
        ).then(
            pl.col('second_half_start') - pl.duration(days=1)
        ).otherwise(
            pl.col('first_half_end')
        ).alias('first_half_end'),

        pl.when(
            pl.col('off_end') < pl.col('off_start')
        ).then(
            None
        ).otherwise(
            pl.col('off_end')
        ).alias('off_end')
    ).with_row_index(name = 'season_id').lazy()

    return lf

def transform_divisions(divisions: pl.LazyFrame,
                        leagues:pl.LazyFrame)-> tuple[pl.LazyFrame, pl.LazyFrame]:
    #construct unique names for divisions with null names
    division_names = divisions.join(
        leagues.select(
            'league_id',
            'league_name',
        ).lazy(),
        left_on='league.id',
        right_on='league_id',
        how='left'
    ).with_columns(
        pl.when(
            pl.col('name').is_null()
        ).then(
            pl.col('league_name') + '(' + pl.col('id').cast(str) + ')'
        ).otherwise(
            pl.col('name')
        ).alias('name')
    ).group_by('id').agg(
        pl.col('name').mode().str.join(' | ').alias('name')
    )

    #join the new names
    div = divisions.select(
        pl.exclude('name', 'sport.id')
    ).join(
        division_names,
        on='id',
        how='left',
    ).select(
        pl.col('id').alias('division_id'),
        pl.col('name').alias('division_name'),
        pl.col('season'),
        pl.col('league.id').alias('league_id'),
        pl.col('active').alias('is_active'),
        pl.col('link').alias('division_link')
    )

    div_seasons = div.select('division_id', 'season')
    div = div.select(
        pl.exclude('season')
    ).unique()
    return div, div_seasons

def transform_teams(lf:pl.LazyFrame)->tuple[pl.LazyFrame, pl.LazyFrame]:
    lf = lf.select(
        pl.col('id').alias('team_id'),
        pl.col('name').alias('team_name'),
        pl.col('league.id').alias('league_id'),
        pl.col('season').alias('year'),
        pl.col('sport.id').alias('sport_id'),
        pl.col('division.id').alias('division_id'),
        pl.col('teamCode').alias('team_code'),
        pl.col('locationName').alias('location_name'),
        pl.col('venue.id').alias('venue_id'),
        pl.col('springLeague.id').alias('spring_league_id'),
        pl.col('springVenue.id').alias('spring_venue_id'),
        pl.col('link').alias('team_link'),
        pl.col('active').alias('is_active'),
        #pl.col('parentOrgId').alias('parent_org_id'),
        ##college teams have parentOrg listed as 11 which is the office of the commissioner, not a team
        pl.when(pl.col('sport.id').eq(22)).then(
            pl.col('parentOrgId').replace(11,None)
        ).otherwise(
            pl.col('parentOrgId')
        ).alias('parent_org_id'),

        pl.col('firstYearOfPlay').alias('first_year')
    )

    name_modes = lf.group_by(
        'team_id'
    ).agg(
        pl.col('location_name').drop_nulls().mode().alias('location_mode'),
    ).with_columns(
        pl.col('location_mode').list.first(),
    )

    lf = lf.join(
        name_modes,
        on='team_id',
        how='left',
    ).with_columns(
        pl.when(
            pl.col('location_name').is_null()
        ).then(
            pl.col('location_mode')
        ).otherwise(
            pl.col('location_name')
        ).alias('location_name')
    ).select(
        cs.exclude('location_mode')
    )

    teams = lf.select(
        ['team_id', 'is_active', 'team_link', 'first_year']
    ).unique()

    teams_seasons = lf.select(
        cs.exclude(['team_link', 'is_active', 'first_year'])
    ).with_row_index(name='squad_id').collect().lazy()
    #materialize the row index: projection pushdown would otherwise drop
    #'squad_id' during lazy validation (ColumnNotFoundError)

    return teams, teams_seasons


