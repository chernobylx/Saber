from statsapi import get as api
import polars as pl
from requests import get as GET
from typing import Callable
url = 'https://statsapi.mlb.com/api/v1/'

def get(endpoint:str)-> pl.DataFrame:

    return endpoints[endpoint]()
def get_sports()-> pl.DataFrame:
    """Retrieve a DataFrame of available sports from the statsapi.mlb.com"""
    try:
        sports = api('sports')['sports']
        sports = pl.json_normalize(sports)
        return sports
    except Exception:
        raise


def get_leagues()-> pl.DataFrame:
    """Retrieve a DataFrame of available leagues from statsapi.mlb.com"""
    try:
        leagues = GET(url+'leagues').json()['leagues']
        leagues = pl.json_normalize(leagues)
        return leagues
    except Exception:
        raise

def get_divisions()-> pl.DataFrame:
    """Retrieve a DataFrame of available divisions from statsapi.mlb.com"""
    try:
        divisions = GET(url+'/divisions').json()['divisions']
        divisions = pl.json_normalize(divisions)
        return divisions
    except Exception:
        raise

endpoints:dict[str, Callable[[],pl.DataFrame]] = {
    'sports': get_sports,
    'leagues': get_leagues,
    'divisions': get_divisions
}
