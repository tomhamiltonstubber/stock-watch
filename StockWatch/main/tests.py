from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse


class SearchCompanySymbolsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_search_company_symbols(self):
        r = self.client.get(reverse('symbol-search'), {'q': 'micro', 'api_key': settings.VANTAGE_API_KEY})
        debug(r.content.decode())
        assert False

    def test_foo(self):
        pass
