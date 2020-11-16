from datetime import datetime

from django import forms

from StockWatch.main.models import Company, StockData
from StockWatch.main.widgets import DatePicker


class SearchStockValidation(forms.Form):
    company = forms.ModelChoiceField(Company.objects.all(), label='')
    date = forms.DateField(label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = DatePicker(self.fields['date'])

    # def clean_date(self):
    #     if date := self.data['date']:
    #         return datetime.strptime(date, '%d/%m/%Y')


class SearchStockForm(forms.ModelForm):
    company = forms.ModelChoiceField(Company.objects.all(), label='')
    date = forms.DateField(label='')
    quantity = forms.IntegerField(label='', min_value=1)
    reference = forms.CharField(label='')
    high = forms.FloatField(widget=forms.HiddenInput)
    low = forms.FloatField(widget=forms.HiddenInput)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = DatePicker(self.fields['date'])
        self.fields['quantity'].widget.attrs['placeholder'] = 'Quantity'
        most_recent = StockData.objects.request_qs(request).first()
        self.fields['reference'].widget.attrs['placeholder'] = 'Reference'
        if most_recent:
            self.fields['reference'].initial = most_recent.reference

    class Meta:
        model = StockData
        fields = 'reference', 'quantity', 'date'
