from django import forms

from StockWatch.main.models import Currency, StockData
from StockWatch.main.widgets import DatePicker


class SearchStockForm(forms.ModelForm):
    symbol = forms.CharField(widget=forms.HiddenInput)
    date = forms.DateField(label='')
    quantity = forms.IntegerField(label='', min_value=1)
    name = forms.CharField(widget=forms.HiddenInput)
    currency = forms.CharField(widget=forms.HiddenInput)
    reference = forms.CharField(label='')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = DatePicker(self.fields['date'])
        self.fields['quantity'].widget.attrs['placeholder'] = 'Quantity'
        most_recent = StockData.objects.request_qs(request).first()
        self.fields['reference'].widget.attrs['placeholder'] = 'Reference'
        if most_recent:
            self.fields['reference'].initial = most_recent.reference

    def clean_currency(self):
        return Currency.objects.get(code=self.cleaned_data['currency'])

    class Meta:
        model = StockData
        fields = 'reference', 'quantity', 'date', 'currency'
