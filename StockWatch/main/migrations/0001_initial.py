# Generated by Django 2.2 on 2019-04-29 20:38

from datetime import datetime
from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import utc
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email Address')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='First name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='Last name')),
                ('last_logged_in', models.DateTimeField(default=datetime(2018, 1, 1, 0, 0, tzinfo=utc), verbose_name='Last Logged in')),
                ('street', models.TextField(blank=True, null=True, verbose_name='Street Address')),
                ('town', models.CharField(blank=True, max_length=50, null=True, verbose_name='Town')),
                ('country', models.CharField(blank=True, max_length=50, null=True, verbose_name='Country')),
                ('postcode', models.CharField(blank=True, max_length=20, null=True, verbose_name='Postcode')),
                ('phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='Phone')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('symbol', models.CharField(max_length=50, verbose_name='Symbol')),
            ],
        ),
        migrations.CreateModel(
            name='Firm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='StockData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Date')),
                ('high', models.DecimalField(decimal_places=6, max_digits=10, verbose_name="Day's high")),
                ('low', models.DecimalField(decimal_places=6, max_digits=10, verbose_name="Day's low")),
                ('quarter', models.DecimalField(decimal_places=6, max_digits=10, verbose_name="Day's quarter")),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Date searched')),
                ('quantity', models.PositiveIntegerField(verbose_name='Volume')),
                ('gross_value', models.DecimalField(decimal_places=6, max_digits=10, verbose_name='Gross Value')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_data', to='main.Company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='firm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Firm', verbose_name='Company'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
