from pathlib import Path

import grablib
from django.conf import settings
from django.contrib.staticfiles.management.commands.collectstatic import Command as CSBaseCommand


class Command(CSBaseCommand):
    def collect(self, **kwargs):
        defpath = Path(settings.BASE_DIR) / 'grablib.yml'
        print('\nrunning grablib...\n')
        grablib.setup_logging('INFO')
        grab = grablib.Grab(str(defpath))
        grab.download()
        grab.build()
        return super().collect(**kwargs)
