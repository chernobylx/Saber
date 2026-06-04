from statsapi import get as api
import polars as pl
from requests import get as GET
from typing import Callable, Iterable
from collections.abc import Iterable
from time import time as now
from time import sleep
from tqdm import tqdm
url = 'https://statsapi.mlb.com/api/v1/'

def get(endpoint:str)-> pl.LazyFrame:

    return endpoints[endpoint]()
def get_sports()-> pl.LazyFrame:
    """Retrieve a DataFrame of available sports from the statsapi.mlb.com"""
    try:
        sports = api('sports')['sports']
        sports = pl.json_normalize(sports)
        return sports.lazy()
    except Exception:
        raise


def get_leagues()-> pl.LazyFrame:
    """Retrieve a DataFrame of available leagues from statsapi.mlb.com"""
    try:
        leagues = GET(url+'leagues').json()['leagues']
        leagues = pl.json_normalize(leagues)
        return leagues.lazy()
    except Exception:
        raise

def get_divisions(years: Iterable[int]=range(2026,1962,-1), sport_id: int=0)-> pl.LazyFrame:
    """Retrieve a DataFrame of available divisions from statsapi.mlb.com"""
    lfs: list[pl.LazyFrame] = []
    fields = ['id','name','season','sport.id','league.id','link','active']
    for year in tqdm(years):
        t = now()
        link = f'{url}/divisions?season={year}'
        if sport_id > 0:
            link += f'&sportId={sport_id}'
        try:
            divisions = GET(link).json()['divisions']
            divisions = pl.json_normalize(divisions).select(fields)
            lfs.append(divisions.lazy())
        except Exception:
            raise
        e = now()-t
        if e < 1:
            sleep(1-e)

    return pl.concat(lfs)

def get_seasons(years: Iterable[int]=range(2026,1893,-1), sport_id: int=0)-> pl.LazyFrame:
    """
    Retrieve season parameters for each league active in a given sport and year (or iterable of years) from statsapi.mlb.com
    If sport_id<=0 then all leagues are returned
    """
    link = f'{url}/leagues?hydrate=schedule&seasons={','.join([str(year)for year in years])}'
    if sport_id>0:
        link += f'&sportId={sport_id}'
    try:
        seasons = GET(link).json()
        seasons = pl.json_normalize(seasons['leagues'])
        return seasons.lazy()
    except Exception:
        raise

endpoints:dict[str, Callable[[],pl.LazyFrame]] = {
    'sports': get_sports,
    'leagues': get_leagues,
    'divisions': get_divisions,
    'seasons': get_seasons
}
