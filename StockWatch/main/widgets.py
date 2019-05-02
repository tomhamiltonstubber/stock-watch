from django.forms import widgets, DateField

DT_OUTER_PICKER_HTML = """\
<div class="input-group date date-picker">
  {}
  <span class="input-group-addon">
    <i class="fa fa-calendar"></i>
  </span>
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
            'data-sideBySide': True
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
        attrs.update({
            'data-date': self._data_value(value, '%Y-%m-%d'),
        })
        return DT_OUTER_PICKER_HTML.format(super().render(name, value, attrs=attrs, renderer=renderer))
