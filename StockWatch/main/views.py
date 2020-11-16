import csv
import decimal
import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import user_logged_in
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import SuspiciousOperation
from django.dispatch import receiver
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import FormView, ListView

from StockWatch.main.eodhistoricaldata import eod_historical_data
from StockWatch.main.forms import SearchStockForm, SearchStockValidation
from StockWatch.main.models import Company, StockData

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
    company_qs = Company.objects.filter(name__icontains=q)
    data = [{'id': id, 'text': name.strip(' ')} for id, name in company_qs.values_list('id', 'name')]
    return JsonResponse(data, safe=False)


@require_POST
@csrf_exempt
def get_historical_price(request):
    form = SearchStockValidation(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        date = cd['date']
        if date.weekday() in {5, 6}:
            if date.weekday() == 5:  # Sat
                date_from = date - timedelta(days=1)
                date_to = date + timedelta(days=3)
            else:  # Date entered is Sunday
                date_from = date - timedelta(days=2)
                date_to = date + timedelta(days=1)
        else:
            date_from = date
            date_to = date
        data = eod_historical_data(symbol=cd['company'].symbol, date_to=date_to, date_from=date_from)
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': form.errors.as_json()}, status=400)


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

    def form_valid(self, form):
        cd = form.cleaned_data
        obj = form.save(commit=False)
        try:
            high = decimal.Decimal(cd['high'])
            low = decimal.Decimal(cd['low'])
            quarter = low + ((high - low) * decimal.Decimal(0.25))
            obj.gross_value = round(quarter * cd['quantity'], 2)
        except decimal.InvalidOperation as e:
            tc_logger.exception(
                'DecimalError caused. %s', e, extra={'stock_data': cd, 'form_data': form.cleaned_data}
            )
            messages.error(self.request, 'Something went wrong there. Please try again.')
            return self.form_invalid(form)
        # TODO: Support different currencies
        obj.company = cd['company']
        obj.currency = obj.company.currency
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
        qs = super().get_queryset().request_qs(self.request).select_related('currency')
        ref = self.request.GET.get('ref')
        if ref:
            qs = qs.filter(reference=ref)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ref_choices = {ref for ref in StockData.objects.request_qs(self.request).values_list('reference', flat=True)}
        return super().get_context_data(
            title=self.title, ref_choices=ref_choices, current_ref=self.request.GET.get('ref', ''), **kwargs
        )


archive = Archive.as_view()


@require_POST
def archive_export(request):
    sd_qs = StockData.objects.request_qs(request).select_related('currency', 'company')
    reference = request.GET.get('ref')
    if reference:
        sd_qs = sd_qs.filter(reference=reference)
    r = HttpResponse(content_type='text/csv')
    r['Content-Disposition'] = 'attachment; filename="export.csv"'
    writer = csv.writer(r)
    writer.writerow(['Reference', 'Company', 'Date', 'High', 'Low', 'Quarter', 'Amount', 'Gross Value', 'currency'])
    for sd in sd_qs:
        writer.writerow(
            [
                sd.reference,
                sd.company.name,
                sd.date,
                sd.high,
                sd.low,
                sd.quarter,
                sd.quantity,
                sd.gross_value,
                sd.currency.code,
            ]
        )
    return r
