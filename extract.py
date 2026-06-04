import polars as pl
from requests import get as GET
from typing import Callable
from collections.abc import Iterable
from time import time as now
from time import sleep
from tqdm import tqdm
from yarl import URL
from joblib import Memory

cache = './.cache'
memory = Memory(cache, verbose=0, compress=6)

api = URL('https://statsapi.mlb.com/api/v1/')
def get(endpoint:str)-> pl.LazyFrame:
    return endpoints[endpoint]()


@memory.cache
def get_lazy_frame(endpoint:str = 'sports', query:dict = None, url:URL = api):
    if query is None:
        query = {}

    url = url/endpoint % query
    try:
        t = now()

        response = GET(str(url))

        e = now()-t
        if e < 1:
            sleep(1-e)

        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}")
        else:
            json = response.json()[endpoint]
            return pl.json_normalize(json).lazy()
    except:
        raise

def get_sports(query:dict=None)-> pl.LazyFrame:
    """Retrieve a DataFrame of available sports from the statsapi.mlb.com
    To get all seasons pass a query without 'season'"""
    if query is None:
        query = {}
    try:
        short_a = get_lazy_frame('sports', {'sportId':15})
        rook_a = get_lazy_frame('sports', {'sportId':5442})
        rest = get_lazy_frame('sports', query=query)
        return pl.concat([rest,short_a, rook_a], how = 'diagonal')
    except:
        raise

def get_leagues(query:dict=None)-> pl.LazyFrame:
    """Retrieve a DataFrame of available leagues from statsapi.mlb.com"""
    if query is None:
        query = {}
    try:
        return get_lazy_frame('leagues', query=query)
    except:
        raise

def get_divisions(years: Iterable[int]=range(2026,1962,-1),
                  sport_id: int=0)-> pl.LazyFrame:
    """Retrieve a DataFrame of available divisions from statsapi.mlb.com
    Earliest season with divisions is 1963"""
    lfs: list[pl.LazyFrame] = []
    if sport_id:
        query = {'sportId': sport_id}
    else:
        query = {}
    #fields = ['id','name','season','league.id','link','active']
    for year in tqdm(years, desc='Divisions'):
        try:
            query['season'] = year
            lfs.append(
                get_lazy_frame(endpoint='divisions', query=query).lazy()
            )
        except:
            raise



    return pl.concat(lfs, how='diagonal')

def get_seasons(years: Iterable[int]=range(2026,1893,-1),
                sport_id: int=0)-> pl.LazyFrame:
    """
    Retrieve season parameters for each league active in a given sport and year
    (or iterable of years) from statsapi.mlb.com
    If sport_id<=0 then all leagues are returned
    """
    query = {}
    if sport_id:
        query['sportId'] = sport_id

    query['hydrate'] = 'schedule'
    query['seasons'] = ','.join([str(year)for year in years])


    try:
        return get_lazy_frame('leagues', query)
    except:
        raise

def get_teams(years: Iterable[int]= range(2026,1870, -1),
              sport_id:int=0,
              use_fields: bool=False)-> pl.LazyFrame:
    lfs: list[pl.LazyFrame] = []
    fields = ['teams','id','name','link','season','venue','location',
              'teamCode','firstYearOfPlay','league','sport', 'division',
              'allStarStatus','parentOrgName','parentOrgId','active','locationName']

    query:dict[str,str|int] = {}
    if sport_id:
        query['sportId'] = sport_id
    elif use_fields:
        query['fields'] = ','.join(fields)


    for year in tqdm(years, desc='Teams'):
        query['season'] = year
        try:
            lfs.append(get_lazy_frame(endpoint='teams', query=query))
        except:
            raise


    return pl.concat(lfs, how='diagonal')


endpoints:dict[str, Callable[[],pl.LazyFrame]] = {
    'sports': get_sports,
    'leagues': get_leagues,
    'divisions': get_divisions,
    'seasons': get_seasons,
    'teams': get_teams
}
