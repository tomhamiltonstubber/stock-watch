import decimal

import requests
from django.conf import settings
from django import forms
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from StockWatch.main.models import StockData, Company

session = requests.Session()


def vantage_request(params: dict):
    base_url = 'https://www.alphavantage.co/query'
    r = session.request('GET', base_url, params={'apikey': settings.VANTAGE_API_KEY, **params})
    if r.status_code != 200:
        raise RuntimeError('Problem accessing URL', r.content.decode())
    return r.json()


def search_company_symbols(request):
    # TODO: Store data in db for quicker access
    params = {'function': 'SYMBOL_SEARCH', 'keywords': request.GET.get('q')}
    data = vantage_request(params)
    return JsonResponse(data)


class StockDetailsForm(forms.Form):
    date = forms.DateField(label='Enter a date')
    symbol = forms.CharField(label='Search for a company symbol')
    name = forms.CharField(widget=forms.HiddenInput, required=False)
    quantity = forms.IntegerField(label='Quantity of stocks', min_value=1)


class StockDetails(FormView):
    template_name = 'search.jinja'
    form_class = StockDetailsForm
    title = 'Search for stock prices'

    def get_context_data(self, **kwargs):
        return super().get_context_data(stock_datas=StockData.objects.all(), **kwargs)

    def form_valid(self, form):
        cd = form.cleaned_data
        params = {'function': 'TIME_SERIES_DAILY', 'symbol': cd['symbol'], 'outputsize': 'compact'}
        data = vantage_request(params)
        stocks_data = data['Time Series (Daily)']
        try:
            stock_data = stocks_data[cd['date'].strftime('%Y-%m-%d')]
        except KeyError:
            dates = list(stocks_data.keys())
            form.add_error(field=None, error=f"As we're only testing, you can only choose from the first 100 records. "
                                             f'We have figures between {dates[0]} - {dates[-1]}')
            return self.form_invalid(form)
        high = decimal.Decimal(stock_data['2. high'])
        low = decimal.Decimal(stock_data['3. low'])
        quarter = low + ((high - low) * decimal.Decimal(0.25))
        gross_value = round(quarter * cd['quantity'], 2)

        company, _ = Company.objects.get_or_create(name=cd['name'], symbol=cd['symbol'])
        StockData.objects.create(company=company, date=cd['date'], high=high, low=low,  # user=self.request.user,
                                 quarter=quarter, quantity=cd['quantity'], gross_value=gross_value)
        return redirect(reverse('search'))


search = StockDetails.as_view()


def create_stock_data(request):
    form = StockDetailsForm(request.GET)
    if not form.is_valid():
        return JsonResponse(form.errors, status=200)

    cd = form.cleaned_data
    # TODO: Use full mode
    params = {'function': 'TIME_SERIES_DAILY', 'symbol': cd['symbol'], 'outputsize': 'compact'}
    data = vantage_request(params)
    stocks_data = data['Time Series (Daily)']
    try:
        stock_data = stocks_data[cd['date'].strftime('%Y-%m-%d')]
    except ValueError:
        return JsonResponse({'error': f'No data exists for that company for that date. '
                            f'We have figures between {stocks_data[0]} - {stocks_data[-1]}'}, status=400)

    high = stock_data['2. high']
    low = stock_data['3. low']
    quarter = (high - low) * 0.25
    gross_value = round(quarter * cd['quantity'], 2)

    company, _ = Company.objects.get_or_create(name=cd['name'], symbol=cd['symbol'])
    StockData.objects.create(user=request.user, company=company, date=cd['date'], high=high, low=low,
                             quarter=quarter, quantity=cd['quantity'], gross_value=gross_value)
    return HttpResponse('ok')
