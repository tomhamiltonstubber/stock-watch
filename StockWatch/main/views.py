import decimal
import logging

from django.contrib import messages
from django.contrib.auth import user_logged_in
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import SuspiciousOperation
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView, ListView

from StockWatch.main.eodhistoricaldata import get_historical_data, symbol_search
from StockWatch.main.forms import SearchStockForm
from StockWatch.main.models import Currency, StockData

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


def search_company_symbols(request):
    q = request.GET.get('q')
    if not q:
        raise SuspiciousOperation('No query to search')
    return JsonResponse(symbol_search(q), safe=False)


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
            symbol_search_url=reverse('symbol-search'),
            **kwargs,
        )
        return ctx

    def form_valid(self, form):
        cd = form.cleaned_data
        stock_data = get_historical_data(form.cleaned_data['date'], cd['company'].symbol)
        if not stock_data:
            form.add_error('__all__', 'No stock data for that day')
            return self.form_invalid(form)
        stock_data = stock_data[0]
        obj = form.save(commit=False)

        try:
            high = decimal.Decimal(stock_data['High'])
            low = decimal.Decimal(stock_data['Low'])
            quarter = low + ((high - low) * decimal.Decimal(0.25))
            obj.gross_value = round(quarter * cd['quantity'], 2)
        except decimal.InvalidOperation as e:
            tc_logger.exception(
                'DecimalError caused. %s', e, extra={'stock_data': stock_data, 'form_data': form.cleaned_data}
            )
            messages.error(self.request, 'Something went wrong there. Please try again.')
            return self.form_invalid(form)
        # TODO: Support different currencies
        obj.currency, _ = Currency.objects.get_or_create(name='Great British Pound', symbol='£', code='GBP')
        obj.company = cd['company']
        obj.high = high
        obj.low = low
        obj.quarter = quarter
        obj.user = self.request.user
        obj.save()
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
