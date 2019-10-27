from django.core.management import BaseCommand

from StockWatch.main.eodhistoricaldata import eod_hd_request
from StockWatch.main.models import Company, Currency


class Command(BaseCommand):
    help = 'Build a list of symbols for an exchange'

    def add_arguments(self, parser):
        parser.add_argument('exchange')

    def handle(self, exchange, *args, **kwargs):
        data = eod_hd_request(f'exchanges/{exchange}/', csv_type=False, fmt='json')
        current_companies = Company.objects.values_list('symbol', flat=True)
        new_companies = []
        currencies = {curr.code: curr for curr in Currency.objects.all()}
        for company in data:
            symbol = company['Code']
            if symbol not in current_companies:
                new_companies.append(
                    Company(
                        symbol=symbol,
                        name=company['Name'],
                        currency=currencies[company['Currency']],
                        country=company['Country'],
                    )
                )
        Company.objects.bulk_create(new_companies)
        print(f'Created {len(new_companies)} new companies')
        print(f'Database currently has {len(current_companies) + len(new_companies)} companies for exchange {exchange}')
