import codecs
import csv
import logging

import requests
from django.conf import settings

session = requests.Session()
logger = logging.getLogger('eodhistorical')


class EodhdRequestError(Exception):
    pass


def eod_hd_request(url, csv_type, **params):
    url_params = {'api_token': settings.EOD_HD_API_KEY, **params}
    r = session.get(f'https://eodhistoricaldata.com/api/{url}', params=url_params)
    r.raise_for_status()
    logger.info('request to %s, params %r', url, params)
    if csv_type:
        reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
        lines = [l for l in reader]
        data = []
        if not lines:
            return data
        headers = lines[0]
        for line in lines[1:-1]:
            data.append(dict(zip(headers, line)))
        return data
    else:
        return r.json()


def eod_historical_data(date_from, date_to, symbol, market='LSE'):
    return eod_hd_request(
        f'eod/{symbol}.{market}/',
        csv_type=True,
        **{'from': date_from.strftime('%Y-%m-%d'), 'to': date_to.strftime('%Y-%m-%d')}
    )
