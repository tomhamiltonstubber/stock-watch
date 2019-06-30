import datetime
from decimal import Decimal
from unittest import mock

import pytest
import responses
from django.urls import reverse

from StockWatch.main.models import Company, Currency, Firm, StockData, User
from StockWatch.main.views import VantageRequestError


@pytest.fixture()
def symbol_search_example():
    return {
        'bestMatches': [
            {
                '1. symbol': 'AUTO.LON',
                '2. name': 'Auto Trader USA',
                '3. type': 'Equity',
                '4. region': 'United States',
                '5. marketOpen': '08:00',
                '6. marketClose': '16:30',
                '7. timezone': 'UTC-05',
                '8. currency': 'USD',
                '9. matchScore': '0.6875',
            },
            {
                '1. symbol': 'AUTO.LON',
                '2. name': 'Auto Trader Group plc',
                '3. type': 'Equity',
                '4. region': 'United Kingdom',
                '5. marketOpen': '08:00',
                '6. marketClose': '16:30',
                '7. timezone': 'UTC+01',
                '8. currency': 'GBP',
                '9. matchScore': '0.6875',
            },
        ]
    }


@pytest.fixture()
def timeseries_example():
    return {
        'meta Data': {
            '1. Information': 'Daily Prices (open, high, low, close) and Volumes',
            '2. Symbol': 'MSFT',
            '3. Last Refreshed': '2019-05-03',
            '4. Output Size': 'Compact',
            '5. Time Zone': 'US/Eastern',
        },
        'Time Series (Daily)': {
            '2019-05-03': {
                '1. open': '127.3600',
                '2. high': '129.4300',
                '3. low': '127.2500',
                '4. close': '128.9000',
                '5. volume': '24911126',
            },
            '2019-05-02': {
                '1. open': '127.9800',
                '2. high': '128.0000',
                '3. low': '125.5200',
                '4. close': '126.2100',
                '5. volume': '27350161',
            },
            '2019-05-01': {
                '1. open': '130.5300',
                '2. high': '130.6500',
                '3. low': '127.7000',
                '4. close': '127.8800',
                '5. volume': '26821692',
            },
            '2019-04-30': {
                '1. open': '129.8100',
                '2. high': '130.7000',
                '3. low': '129.3947',
                '4. close': '130.6000',
                '5. volume': '24166503',
            },
            '2019-04-29': {
                '1. open': '129.9000',
                '2. high': '130.1800',
                '3. low': '129.3500',
                '4. close': '129.7700',
                '5. volume': '16324183',
            },
            '2019-04-26': {
                '1. open': '129.7000',
                '2. high': '130.5152',
                '3. low': '129.0200',
                '4. close': '129.8900',
                '5. volume': '23654933',
            },
            '2019-04-25': {
                '1. open': '130.0600',
                '2. high': '131.3700',
                '3. low': '128.8300',
                '4. close': '129.1500',
                '5. volume': '38033892',
            },
        },
    }


@pytest.fixture()
def auth_client(client):
    user = User.objects.create_user(
        first_name='Tom',
        last_name='Owner',
        email='testing@stockwatch.com',
        password='testing',
        firm=Firm.objects.create(name='123 Firm Ltd'),
    )
    logged_in = client.login(username=user.email, password='testing')
    assert logged_in, 'Not logged in'
    Currency.objects.create(code='GBP', name='GBP', symbol='£')
    return client


def assert_redirects(r, url):
    assert hasattr(r, 'redirect_chain'), 'Response was not a redirect. Did you use follow=True?'
    response_url, _ = r.redirect_chain[0]
    assert response_url == url, 'Response redirected to wrong page: ' + response_url


@pytest.mark.django_db
def test_redirect_not_authed(client):
    User.objects.create_user(
        first_name='Tom',
        last_name='Owner',
        email='testing@stockwatch.com',
        password='testing',
        firm=Firm.objects.create(name='123 Firm Ltd'),
    )
    r = client.get('/', follow=True)
    assert_redirects(r, '/login/')


@pytest.mark.django_db
def test_login(client):
    User.objects.create_user(
        first_name='Tom',
        last_name='Owner',
        email='testing@stockwatch.com',
        password='testing',
        firm=Firm.objects.create(name='123 Firm Ltd'),
    )
    r = client.post('/login/', data={'username': 'testing@stockwatch.com', 'password': 'testing'}, follow=True)
    assert_redirects(r, '/')


@pytest.mark.django_db
def test_logout(auth_client):
    r = auth_client.post(reverse('logout'), follow=True)
    assert_redirects(r, '/login/')
    r = auth_client.get('/', follow=True)
    assert_redirects(r, '/login/')


@pytest.mark.django_db
@responses.activate
def test_search_symbols_ordered(auth_client, symbol_search_example):
    responses.add('GET', 'https://www.alphavantage.co/query', json=symbol_search_example)
    r = auth_client.get(reverse('symbol-search'), {'q': 'auto trader'})
    assert r.json() == [
        {'symbol': 'AUTO.LON', 'name': 'Auto Trader Group plc', 'region': 'United Kingdom', 'currency': 'GBP'},
        {'symbol': 'AUTO.LON', 'name': 'Auto Trader USA', 'region': 'United States', 'currency': 'USD'},
    ]


@pytest.mark.django_db
@responses.activate
def test_search_symbol_vantage_error(auth_client):
    responses.add('GET', 'https://www.alphavantage.co/query', json={'Error Message': 'Foo'})
    with pytest.raises(VantageRequestError):
        auth_client.get(reverse('symbol-search'), {'q': 'auto trader'})


@pytest.mark.django_db
@responses.activate
def test_search_symbol_bad_response(auth_client):
    responses.add('GET', 'https://www.alphavantage.co/query', body='There was an error', status=500)
    with pytest.raises(VantageRequestError):
        auth_client.get(reverse('symbol-search'), {'q': 'auto trader'})


@pytest.mark.django_db
@responses.activate
def test_timeseries_options(auth_client, timeseries_example):
    responses.add('GET', 'https://www.alphavantage.co/query', json=timeseries_example)
    url = reverse('search')
    r = auth_client.get(url)
    assert r.status_code == 200
    r = auth_client.post(
        url,
        data={
            'date': datetime.date(2019, 4, 30).strftime('%d/%m/%Y'),
            'symbol': 'AUTO.LON',
            'quantity': 2,
            'name': 'Auto Trader London Office',
            'currency': 'GBP',
            'reference': 'Client 1',
        },
    )
    assert r.status_code == 302
    sd = StockData.objects.get()
    assert sd.high == Decimal('130.7000')
    assert sd.date == datetime.date(2019, 4, 30)
    assert sd.company == Company.objects.get(name='Auto Trader London Office')
    r = auth_client.get(url)
    assert sd.company.name in r.content.decode()
    assert 'value="Client 1"' in r.content.decode()


@pytest.mark.django_db
@responses.activate
def test_timeseries_weekend(auth_client, timeseries_example):
    responses.add('GET', 'https://www.alphavantage.co/query', json=timeseries_example)
    url = reverse('search')
    r = auth_client.get(url)
    assert r.status_code == 200
    r = auth_client.post(
        url,
        data={
            'date': datetime.date(2019, 4, 28).strftime('%d/%m/%Y'),
            'symbol': 'AUTO.LON',
            'quantity': 2,
            'name': 'Auto Trader London Office',
            'currency': 'GBP',
            'reference': 'Client 1',
        },
    )
    assert r.status_code == 302
    sd = StockData.objects.get()
    assert sd.high == Decimal('130.5152')
    assert sd.date == datetime.date(2019, 4, 28)
    assert sd.currency == Currency.objects.get(symbol='£')
    assert sd.company == Company.objects.get(name='Auto Trader London Office')
    assert sd.user == User.objects.get()
    r = auth_client.get(url)
    assert sd.company.name in r.content.decode()


@pytest.mark.django_db
@responses.activate
def test_timeseries_out_of_range(auth_client, timeseries_example):
    responses.add('GET', 'https://www.alphavantage.co/query', json=timeseries_example)
    url = reverse('search')
    r = auth_client.get(url)
    assert r.status_code == 200
    r = auth_client.post(
        url,
        data={
            'date': datetime.date(2019, 4, 24).strftime('%d/%m/%Y'),
            'symbol': 'AUTO.LON',
            'quantity': 2,
            'name': 'Auto Trader London Office',
            'currency': 'GBP',
            'reference': 'Client 1',
        },
    )
    assert r.status_code == 200
    assert 'We have figures between 2019-04-25 - 2019-05-03' in r.content.decode()
    assert not StockData.objects.exists()


@pytest.mark.django_db
@responses.activate
def test_decimal_error(auth_client):
    mock_data = {
        'meta Data': {
            '1. Information': 'Daily Prices (open, high, low, close) and Volumes',
            '2. Symbol': 'MSFT',
            '3. Last Refreshed': '2019-05-03',
            '4. Output Size': 'Compact',
            '5. Time Zone': 'US/Eastern',
        },
        'Time Series (Daily)': {
            '2019-05-03': {
                '1. open': '127.3600',
                '2. high': '551.2000',
                '3. low': 'foobar',
                '4. close': '128.9000',
                '5. volume': '24911126',
            }
        },
    }
    responses.add('GET', 'https://www.alphavantage.co/query', json=mock_data)
    r = auth_client.post(
        reverse('search'),
        data={
            'date': datetime.date(2019, 5, 3).strftime('%d/%m/%Y'),
            'symbol': 'AUTO.LON',
            'quantity': 2,
            'name': 'Auto Trader London Office',
            'currency': 'GBP',
            'reference': 'this',
        },
    )
    assert 'Something went wrong' in r.content.decode()


@pytest.mark.django_db
def test_real_vantage_time_series(auth_client):
    data = {
        'date': datetime.date.today().strftime('%d/%m/%Y'),
        'symbol': 'AUTO.LON',
        'quantity': 2,
        'currency': 'GBP',
        'name': 'AutoTrader',
        'reference': 'Client 1',
    }
    r = auth_client.post(reverse('search'), data=data)
    assert r.status_code == 302


@pytest.mark.django_db
def test_real_vantage_symbol_search(auth_client):
    r = auth_client.get(reverse('symbol-search'), {'q': 'microsoft'})
    assert r.status_code == 200
