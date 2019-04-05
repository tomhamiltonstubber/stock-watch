import requests
from django.conf import settings
from django import forms
from django.views.generic import FormView

session = requests.Session()


def vantage_request(company):
    base_url = 'https://www.alphavantage.co/query'
    params = {'function': 'TIME_SERIES_DAILY', 'symbol': company, 'apikey': settings.VANTAGE_API_KEY}
    r = session.request('GET', base_url, params=params)
    if not r.status_code == 200:
        raise RuntimeError('Problem accessing URL', r.content.decode())
    return r.json()


class StockDetailsForm(forms.Form):
    date = forms.DateField(label='Enter a date')
    company_symbol = forms.CharField(label='Enter the company symbol')


class StockDetails(FormView):
    template_name = 'standard.jinja'
    form_class = StockDetailsForm

    def get_context_data(self, **kwargs):
        if self.request.GET:
            self.form = self.form_class(data=self.request.GET)
            self.form.full_clean()
        else:
            self.form = self.form_class()

        symbol = self.request.GET.get('symbol')
        date = self.request.GET.get('date')
        if symbol:
            data = vantage_request(symbol, date)
            return super().get_context_data(data=data, **kwargs)


stock_details = StockDetails.as_view()


class StockDetailsFormView(FormView):
    template_name = 'form.jinja'
    form_class = StockDetailsForm

    def form_valid(self, form):
        return
