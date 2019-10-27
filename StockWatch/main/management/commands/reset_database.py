import shutil

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import DEFAULT_DB_ALIAS, connections


class Command(BaseCommand):
    help = 'Recreates database schema'

    def add_arguments(self, parser):
        parser.add_argument('--demo-data', action='store_true', dest='demo_data', default=True, help='')

    def handle(self, demo_data, *args, **options):
        if input('Are you sure you want to DESTROY ALL DATA irreversibly? [yes/NO] ') != 'yes':
            print('Cancelled')
            return

        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

        cur = connections[DEFAULT_DB_ALIAS].cursor()
        cur.execute('DROP SCHEMA public CASCADE;')
        cur.execute('CREATE SCHEMA public;')

        call_command('migrate', run_syncdb=True)
        call_command('update_currencies')
        call_command('update_symbols', 'LSE')
        if demo_data:
            print('creating demo data')
            call_command('create_demo_data')
