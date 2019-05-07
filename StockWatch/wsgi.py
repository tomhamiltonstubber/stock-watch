import os

from django.core.wsgi import get_wsgi_application  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StockWatch.settings")

application = get_wsgi_application()
