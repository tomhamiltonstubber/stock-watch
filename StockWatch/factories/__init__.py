import factory
from factory import DjangoModelFactory

from StockWatch.main.models import Company


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: 'Company %d' % n)
    symbol = factory.Sequence(lambda n: 'CO%d' % n)
    country = factory.Sequence(lambda n: 'X%d' % n)
