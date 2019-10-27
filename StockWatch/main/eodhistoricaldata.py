import codecs
import csv
import logging

import requests
from django.conf import settings
from requests import HTTPError

session = requests.Session()
logger = logging.getLogger('eodhistorical')


class EodhdRequestError(Exception):
    pass


def eod_hd_request(url, **params):
    url_params = {'api_token': settings.EOD_HD_API_KEY, **params}
    try:
        r = session.get(f'https://eodhistoricaldata.com/api/{url}', params=url_params)
        r.raise_for_status()
    except HTTPError as e:
        raise EodhdRequestError('Problem accessing URL', e)
    logger.info('request to %s, params %r', url, params)
    reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
    lines = [l for l in reader]
    data = []
    if not lines:
        return data
    headers = lines[0]
    for line in lines[1:-1]:
        data.append(dict(zip(headers, line)))
    return data


def get_historical_data(date, symbol, market='LSE'):
    date = date.strftime('%Y-%m-%d')
    data = eod_hd_request(f'eod/{symbol}.{market}/', **{'from': date, 'to': date})
    return data