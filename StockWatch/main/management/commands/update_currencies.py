import requests
from django.core.management import BaseCommand

from StockWatch.main.models import Currency


class Command(BaseCommand):
    help = 'watch and build scss files'

    def handle(self, **kwargs):
        r = requests.get('https://raw.githubusercontent.com/wiredmax/world-currencies/master/dist/json/currencies.json')
        assert r.status_code == 200, 'bad response: ' + r.status_code
        current_currencies = list(Currency.objects.values_list('code', flat=True))
        new_currencies = []
        for code, deets in r.json().items():
            if code not in current_currencies:
                name = deets['name'].split(' or ')[-1].split(', ')[-1]
                symbol = deets['units']['major']['symbol'].split(' or ')[-1].split(', ')[-1]
                if not name or not symbol:
                    continue
                new_currencies.append(Currency(code=code, name=name, symbol=symbol))
        if 'GBX' not in current_currencies:
            new_currencies.append(Currency(code='GBX', name='Pence Stirling', symbol='p', zero_currency=True))
        if 'USX' not in current_currencies:
            new_currencies.append(Currency(code='USX', name='US cents', symbol='c', zero_currency=True))
        Currency.objects.bulk_create(new_currencies)
        print(f'Created {len(new_currencies)} new currencies')
        print(f'Database currently has {len(current_currencies) + len(new_currencies)} currencies')
