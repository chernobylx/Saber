from statsapi import get
import polars as pl

def get_sports()-> pl.DataFrame:
    """Retrieve a DataFrame of available sports from the statsapi.mlb.com"""
    try:
        sports = get('sports')['sports']
        sports = pl.json_normalize(sports)
        return sports
    except Exception as e:
        raise