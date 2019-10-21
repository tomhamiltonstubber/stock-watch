from datetime import timedelta

import requests

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse


class VantageRequestError(Exception):
    pass


session = requests.Session()


def vantage_request(params: dict):
    base_url = 'https://www.alphavantage.co/query'
    r = session.request('GET', base_url, params={'apikey': settings.VANTAGE_API_KEY, **params})
    if r.status_code != 200:
        raise VantageRequestError('Problem accessing URL', r.content.decode())
    data = r.json()
    if data.get('Note'):
        raise VantageRequestError("We've used up all our API calls. Try again in a few minutes.")
    errors = data.get('Error Message')
    if errors:
        raise VantageRequestError('Error accessing Vantage (%s): %r' % (r.url, errors))
    return data


REGION_ORDER = {'United Kingdom': 1, 'United States': 2}


def search_company_symbols(request):
    params = {'function': 'SYMBOL_SEARCH', 'keywords': request.GET.get('q')}
    r = vantage_request(params)
    data = [
        {'symbol': d['1. symbol'], 'name': d['2. name'], 'region': d['4. region'], 'currency': d['8. currency']}
        for d in r['bestMatches']
    ]
    data = sorted(data, key=lambda x: REGION_ORDER.get(x['region'], 10))
    return JsonResponse(data, safe=False)


def get_stock_data(date, symbol):
    params = {'function': 'TIME_SERIES_DAILY', 'symbol': symbol, 'outputsize': 'compact'}
    data = vantage_request(params)
    stocks_data = data['Time Series (Daily)']
    days = 0
    stock_data = None
    while not stock_data:
        # The market is closed on bank hols and public holidays
        date = (date - timedelta(days=days)).strftime('%Y-%m-%d')
        stock_data = stocks_data.get(date)
        if stock_data:
            return stock_data
        if days == 7:
            dates = list(stocks_data.keys())
            raise ValidationError(
                f"As we're only testing, you can only choose from the first 100 records." 
                f"We have figures between {dates[-1]} - {dates[0]}",
            )
        days += 1
    return stock_data
