from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.datetime_safe import datetime


class Company(models.Model):
    objects = QuerySet.as_manager()

    name = models.CharField('Name', max_length=255)
    symbol = models.CharField('Symbol', max_length=50)

    def __str__(self):
        return f'{self.name} ({self.symbol})'


class Firm(models.Model):
    objects = QuerySet.as_manager()

    name = models.CharField('Name', max_length=255)


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, firm, password, **extra_fields):
        return self._create_user(email=email, password=password, is_superuser=False, firm=firm, **extra_fields)

    def create_super_user(self, email, password, **extra_fields):
        return self._create_user(email=email, password=password, is_superuser=True, **extra_fields)


class User(AbstractUser):
    objects = UserManager()

    username = None
    email = models.EmailField('Email Address', unique=True)
    first_name = models.CharField('First name', max_length=30, blank=True)
    last_name = models.CharField('Last name', max_length=150, blank=True)
    last_logged_in = models.DateTimeField('Last Logged in', default=datetime(2018, 1, 1, tzinfo=timezone.utc))
    street = models.TextField('Street Address', null=True, blank=True)
    town = models.CharField('Town', max_length=50, null=True, blank=True)
    country = models.CharField('Country', max_length=50, null=True, blank=True)
    postcode = models.CharField('Postcode', max_length=20, null=True, blank=True)
    phone = models.CharField('Phone', max_length=255, null=True, blank=True)
    firm = models.ForeignKey(
        Firm, verbose_name='Company', related_name='users', null=True, blank=True, on_delete=models.CASCADE
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Currency(models.Model):
    objects = QuerySet.as_manager()

    name = models.CharField('Name', max_length=255, unique=True)
    code = models.CharField('Code', max_length=3, unique=True)
    symbol = models.CharField('Symbol', max_length=5)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'


class StockDataQS(QuerySet):
    def request_qs(self, request):
        if not request.user.is_authenticated:
            return StockData.objects.none()
        return StockData.objects.filter(user=request.user)


class StockData(models.Model):
    objects = StockDataQS.as_manager()

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
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

    class Meta:
        ordering = ['-timestamp']
