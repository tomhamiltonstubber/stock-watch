import decimal
import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import user_logged_in
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView, ListView

from StockWatch.main.forms import SearchStockForm
from StockWatch.main.models import Company, StockData

session = requests.Session()

tc_logger = logging.getLogger('SW')


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
    if data.get('Note'):
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
    data = [
        {'symbol': d['1. symbol'], 'name': d['2. name'], 'region': d['4. region'], 'currency': d['8. currency']}
        for d in r['bestMatches']
    ]
    data = sorted(data, key=lambda x: REGION_ORDER.get(x['region'], 10))
    return JsonResponse(data, safe=False)


class Search(FormView):
    template_name = 'search.jinja'
    form_class = SearchStockForm
    title = 'Search for stock prices'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(
            stock_datas=StockData.objects.request_qs(self.request).select_related('currency')[:10],
            title=self.title,
            **kwargs,
        )
        return ctx

    def get_stock_data(self, form):
        params = {'function': 'TIME_SERIES_DAILY', 'symbol': form.cleaned_data['symbol'], 'outputsize': 'compact'}
        data = vantage_request(params)
        stocks_data = data['Time Series (Daily)']
        days = 0
        stock_data = None
        while not stock_data:
            # The market is closed on bank hols and public holidays
            date = (form.cleaned_data['date'] - timedelta(days=days)).strftime('%Y-%m-%d')
            stock_data = stocks_data.get(date)
            if stock_data:
                return stock_data
            if days == 7:
                dates = list(stocks_data.keys())
                form.add_error(
                    field=None,
                    error=f"As we're only testing, you can only choose from the first 100 records. "
                    f'We have figures between {dates[-1]} - {dates[0]}',
                )
                return
            days += 1

    def form_valid(self, form):
        stock_data = self.get_stock_data(form)
        if not stock_data:
            return self.form_invalid(form)
        company, _ = Company.objects.get_or_create(name=form.cleaned_data['name'], symbol=form.cleaned_data['symbol'])
        obj = form.save(commit=False)

        try:
            high = decimal.Decimal(stock_data['2. high'])
            low = decimal.Decimal(stock_data['3. low'])
            quarter = low + ((high - low) * decimal.Decimal(0.25))
            obj.company = company
            obj.high = high
            obj.low = low
            obj.quarter = quarter
            obj.gross_value = round(quarter * form.cleaned_data['quantity'], 2)
            obj.user = self.request.user
            obj.save()
        except decimal.InvalidOperation as e:
            tc_logger.exception(
                'DecimalError caused. %s', e, extra={'stock_data': stock_data, 'form_data': form.cleaned_data}
            )
            messages.error(self.request, 'Something went wrong there. Please try again.')
            return self.form_invalid(form)
        return redirect(reverse('search'))


search = Search.as_view()


class Archive(ListView):
    template_name = 'archive.jinja'
    model = StockData
    title = 'Previous Searches'

    def get_queryset(self):
        return super().get_queryset().request_qs(self.request).select_related('currency')

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(title=self.title)


archive = Archive.as_view()
