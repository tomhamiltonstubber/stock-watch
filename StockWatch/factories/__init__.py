import datetime
import decimal

import factory
from factory import DjangoModelFactory, fuzzy

from StockWatch.main.models import Company, Firm, StockData, User


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: 'Company %d' % n)
    symbol = factory.Sequence(lambda n: 'CO%d' % n)
    country = fuzzy.FuzzyText(length=2)


class FirmFactory(DjangoModelFactory):
    class Meta:
        model = Firm

    name = factory.Sequence(lambda n: 'branch %d' % n)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    password = 'testing'
    firm = factory.SubFactory(FirmFactory)
    last_name = factory.Sequence(lambda n: 'last_name_%d' % n)

    @factory.LazyAttribute
    def email(self):
        fn = getattr(self, 'first_name', 'Brain')
        ln = self.last_name
        em = '%s_%s@example.com' % (fn, ln)
        return em.lower().replace(' ', '_')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class StockDataFactory(DjangoModelFactory):
    class Meta:
        model = StockData

    user = factory.SubFactory(UserFactory)
    company = factory.SubFactory(CompanyFactory, currency=factory.SelfAttribute('..currency'))
    date = datetime.datetime(2014, 1, 1, tzinfo=datetime.timezone.utc)
    high = 400
    low = 200
    quarter = low + ((high - low) * decimal.Decimal(0.25))
    quantity = 1
    gross_value = quarter * quantity
    reference = factory.Sequence(lambda n: 'Ref %d' % n)
