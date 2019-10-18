import csv

from django.core.management import BaseCommand

from StockWatch.main.models import Company


class Command(BaseCommand):
    help = 'Rebuild list of companies + their symbols'

    def handle(self, **kwargs):
        companies = []
        with open('XLON_metadata.csv') as f:
            reader = csv.reader(f)
            for i, (symbol, name, *args) in enumerate(reader):
                if i == 1:
                    pass
                companies.append(Company(name=name, symbol=symbol))
        Company.objects.bulk_create(companies)
