from urllib.parse import urlencode

import requests
from django.conf import settings

session = requests.Session()


class QuandlRequestError(Exception):
    pass


def quandl_request(url, **params):
    params = {'api_key': settings.QUANDL_API_KEY, **params}
    r = session.get(f'https://www.quandl.com/api/v3/{url}?{urlencode(params)}')
    if r.status_code != 200:
        raise QuandlRequestError('Problem accessing URL', r.content.decode())
    return r.json()


def get_historical_data(date, symbol, market='XLON'):
    date = date.strftime('%Y-%m-%d')
    return quandl_request(f'datasets/{market}/{symbol}/', start_date=date, end_date=date)
