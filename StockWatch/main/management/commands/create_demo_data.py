from django.core.management import BaseCommand

from StockWatch.main.models import Firm, User


class Command(BaseCommand):
    help = 'Creates demo data'

    def handle(self, *args, **opts):
        firm = Firm.objects.create(name='Demo Firm')
        User.objects.create_user(
            first_name='Brian', last_name='Cranston', password='Br3@k1ngB@d', firm=firm, email='testing@sorom.com'
        )
        print('Created user with details:\n  email: testing@sorom.com\n  password: Br3@k1ngB@d')
