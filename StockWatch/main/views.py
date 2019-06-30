import decimal
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib.auth import user_logged_in
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView

from django import forms
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView

from StockWatch.main.models import StockData, Company, Currency
from StockWatch.main.widgets import DatePicker

session = requests.Session()


class Login(LoginView):
    title = 'Login'
    template_name = 'login.jinja'
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def get_redirect_url(self):
        return reverse('search')

    def get_context_data(self, **kwargs):
        return super().get_context_data(title=self.title, **kwargs)


login = Login.as_view()


@receiver(user_logged_in)
def update_user_history(sender, user, **kwargs):
    user.last_logged_in = timezone.now()
    user.save(update_fields=['last_logged_in'])


class VantageRequestError(Exception):
    pass


def vantage_request(params: dict):
    base_url = 'https://www.alphavantage.co/query'
    r = session.request('GET', base_url, params={'apikey': settings.VANTAGE_API_KEY, **params})
    if r.status_code != 200:
        raise VantageRequestError('Problem accessing URL', r.content.decode())
    data = r.json()
    if data.get('note'):
        raise VantageRequestError("We've used up all our API calls. Try again in a few minutes.")
    errors = data.get('Error Message')
    if errors:
        raise VantageRequestError('Error accessing Vantage (%s): %r' % (r.url, errors))
    return data


REGION_ORDER = {'United Kingdom': 1, 'United States': 2}


def search_company_symbols(request):
    # TODO: Store data in db for quicker access
    params = {'function': 'SYMBOL_SEARCH', 'keywords': request.GET.get('q')}
    r = vantage_request(params)
    data = [{
        'symbol': d['1. symbol'],
        'name': d['2. name'],
        'region': d['4. region'],
        'currency': d['8. currency'],
    } for d in r['bestMatches']]
    data = sorted(data, key=lambda x: REGION_ORDER.get(x['region'], 10))
    return JsonResponse(data, safe=False)


class SearchStockForm(forms.Form):
    symbol = forms.CharField(widget=forms.HiddenInput)
    date = forms.DateField(label='')
    quantity = forms.IntegerField(label='', min_value=1)
    name = forms.CharField(widget=forms.HiddenInput)
    currency = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = DatePicker(self.fields['date'])
        self.fields['quantity'].widget.attrs['placeholder'] = 'Quantity'

    def clean_currency(self):
        return Currency.objects.get(code=self.cleaned_data['currency'])


class Search(FormView):
    template_name = 'search.jinja'
    form_class = SearchStockForm
    title = 'Search for stock prices'

    def get_context_data(self, **kwargs):
        return super().get_context_data(stock_datas=StockData.objects.order_by('-id')[:20], title=self.title, **kwargs)

    def form_valid(self, form):
        cd = form.cleaned_data
        params = {'function': 'TIME_SERIES_DAILY', 'symbol': cd['symbol'], 'outputsize': 'compact'}
        data = vantage_request(params)
        stocks_data = data['Time Series (Daily)']
        stock_data = None
        for i in range(7):
            # The market is closed on bank hols and public holidays
            date = (cd['date'] - timedelta(days=i)).strftime('%Y-%m-%d')
            stock_data = stocks_data.get(date)
            if stock_data:
                break
        if not stock_data:
            dates = list(stocks_data.keys())
            form.add_error(field=None, error=f"As we're only testing, you can only choose from the first 100 records. "
                                             f'We have figures between {dates[-1]} - {dates[0]}')
            return self.form_invalid(form)
        high = decimal.Decimal(stock_data['2. high'])
        low = decimal.Decimal(stock_data['3. low'])
        quarter = low + ((high - low) * decimal.Decimal(0.25))
        gross_value = round(quarter * cd['quantity'], 2)

        company, _ = Company.objects.get_or_create(name=cd['name'], symbol=cd['symbol'])
        StockData.objects.create(company=company, date=cd['date'], high=high, low=low,  user=self.request.user,
                                 quarter=quarter, quantity=cd['quantity'], gross_value=gross_value,
                                 currency=cd['currency'])
        return redirect(reverse('search'))


search = Search.as_view()
