from django.apps import AppConfig


class StaticFilesConfig(AppConfig):
    name = 'StockWatch.staticfiles'
    label = 'StockWatch.sw_staticfiles'


default_app_config = 'StockWatch.staticfiles.StaticFilesConfig'
