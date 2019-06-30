import datetime

from django.forms import DateField, widgets
from django.utils.timezone import now

DT_OUTER_PICKER_HTML = """\
<div class="input-group date date-time-picker" data-target-input="nearest" id="{id}">
  {input}
  <div class="input-group-append" data-target="#{id}" data-toggle="datetimepicker">
    <div class="input-group-text"><i class="fa fa-calendar"></i></div>
  </div>
</div>"""


class DatePicker(widgets.DateInput):
    format = 'DD/MM/YYYY'

    def __init__(self, field):
        self._is_datetime = False
        assert isinstance(field, DateField)
        attrs = {
            'data-type': 'date',
            'data-format': self.format,
            'data-minDate': '1900-01-01',
            'data-sideBySide': True,
            'data-yesterday': (now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
        }
        formats = ['%d/%m/%Y']
        self._is_datetime = True
        super().__init__(attrs, self.format)
        field.input_formats = formats

    def _data_value(self, value, format):
        if not value:
            return ''
        elif isinstance(value, str):
            return value
        else:
            return value.strftime(format)

    def render(self, name, value, attrs=None, renderer=None):
        attrs.update(
            {
                'data-date': self._data_value(value, '%Y-%m-%d'),
                'data-target': '#' + name,
                'class': 'form-control datetimepicker-input',
            }
        )
        return DT_OUTER_PICKER_HTML.format(
            input=super().render(name, value, attrs=attrs, renderer=renderer), id='datepicker-' + name
        )
