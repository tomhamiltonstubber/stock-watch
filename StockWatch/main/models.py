from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.datetime_safe import datetime


class Equity(models.Model):
    name = models.CharField('Name', max_length=255)
    address = models.CharField('Address', null=True, blank=True, max_length=512)
    symbol = models.CharField('Symbol')

    def __str__(self):
        return f'{self.name} ({self.symbol})'


class StockData(models.Model):
    corporate_entity = models.ForeignKey(Equity, on_delete=models.CASCADE, related_name='stock_data')
    date = models.DateField('Date')
    high = models.DecimalField("Day's high", decimal_places=6)
    low = models.DecimalField("Day's low", decimal_places=6)
    quarter = models.DecimalField("Day's quarter", decimal_places=6)


class Company(models.Model):
    name = models.CharField('Name', max_length=255)


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, company, password, **extra_fields):
        return self._create_user(email=email, password=password, company=company **extra_fields)


class User(AbstractUser):
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
    company = models.ForeignKey(Company, verbose_name='Company', on_delete=models.CASCADE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
