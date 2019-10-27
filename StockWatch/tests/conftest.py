import pytest

from StockWatch.main.models import Currency, Firm, User


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
    Currency.objects.create(code='GBP', name='Great British Pound', symbol='£')
    return client


@pytest.fixture()
def timeseries_example():
    return 'Date,Open,High,Low,Close,Adjusted_close,Volume\n2019-1-4,100,800,500,500,500,3903565\n??'


@pytest.fixture()
def timeseries_example_bad():
    return 'Date,Open,High,Low,Close,Adjusted_close,Volume\n2019-1-4,100,800,FOOBAR,500,500,3903565\n??'