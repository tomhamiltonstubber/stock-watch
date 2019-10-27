import factory
from factory import DjangoModelFactory

from StockWatch.main.models import Company, Firm, StockData, User


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: 'Company %d' % n)
    symbol = factory.Sequence(lambda n: 'CO%d' % n)
    country = factory.Sequence(lambda n: 'X%d' % n)


class FirmFactory(DjangoModelFactory):
    class Meta:
        model = Firm

    name = factory.Sequence(lambda n: 'branch %d' % n)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    password = 'testing'
    firm = factory.SubFactory(FirmFactory)
    last_name = factory.Sequence(lambda n: 'last_namé_%d' % n)

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
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stock_data')
    date = models.DateField('Date')
    high = models.DecimalField("Day's high", decimal_places=6, max_digits=20)
    low = models.DecimalField("Day's low", decimal_places=6, max_digits=20)
    quarter = models.DecimalField("Day's quarter", decimal_places=6, max_digits=20)
    timestamp = models.DateTimeField('Date searched', auto_now_add=True)
    quantity = models.PositiveIntegerField('Volume')
    gross_value = models.DecimalField('Gross Value', decimal_places=6, max_digits=20)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    reference = models.CharField('Reference', max_length=255)
