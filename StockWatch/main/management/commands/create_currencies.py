import requests

from django.core.management import BaseCommand

from StockWatch.main.models import Currency


class Command(BaseCommand):
    help = 'watch and build scss files'

    def handle(self, **kwargs):
        r = requests.get('https://raw.githubusercontent.com/wiredmax/world-currencies/master/dist/json/currencies.json')
        assert r.status_code == 200, 'bad response: ' + r.status_code
        old_currencies = list(Currency.objects.values_list('code', flat=True))
        for code, deets in r.json().items():
            if code not in old_currencies:
                name = deets['name'].split(' or ')[-1].split(', ')[-1]
                symbol = deets['units']['major']['symbol'].split(' or ')[-1].split(', ')[-1]
                if not name or not symbol:
                    continue
                Currency.objects.create(code=code, name=name, symbol=symbol)
