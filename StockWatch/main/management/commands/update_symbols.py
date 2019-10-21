import csv
import glob
import os
import zipfile

import wget
from django.conf import settings

from django.core.management import BaseCommand

from StockWatch.main.models import Company

PATH = 'data/'
FILE = 'XLON_metadata'


class Command(BaseCommand):
    help = 'Rebuild list of companies + their symbols'

    def handle(self, **kwargs):
        files = glob.glob(PATH + '*')
        for f in files:
            os.remove(f)
        companies = []
        url = 'https://www.quandl.com/api/v3/databases/XLON/metadata?api_key=' + settings.QUANDL_API_KEY
        wget.download(url, PATH + FILE + '.zip')
        with zipfile.ZipFile(PATH + FILE + '.zip') as zf:
            zf.extractall(PATH)
        current_companies = list(Company.objects.values_list('symbol', flat=True))
        print('\nFiles downloaded, updating companies')
        with open(PATH + FILE + '.csv') as f:
            reader = csv.reader(f)
            for i, (symbol, name, *args) in enumerate(reader):
                if i == 0:
                    continue
                if symbol not in current_companies:
                    companies.append(Company(name=name, symbol=symbol))
        Company.objects.bulk_create(companies)
        print(f'Created {len(companies)} new companies')
        print(f'Database currently has {len(current_companies)} companies')
