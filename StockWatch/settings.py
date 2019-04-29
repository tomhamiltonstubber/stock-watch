import os

DJ_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(DJ_DIR)

SECRET_KEY = os.getenv('SECRET_KEY', '4d2a5e6514c95192aacab316ef5c0706')

DEBUG = os.getenv('DEBUG', True)
LIVE = os.getenv('LIVE')

ALLOWED_HOSTS = []

VANTAGE_API_KEY = os.getenv('VANTAGE_API_KEY')

AUTH_USER_MODEL = 'main.User'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_jinja',
    'django_extensions',
    'bootstrap3_datetime',
    'bootstrapform_jinja',
    'debug_toolbar',
    'raven.contrib.django.raven_compat',

    'StockWatch.main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'StockWatch.urls'

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,
        'DIRS': ['templates'],
        "OPTIONS": {
            "match_extension": ".jinja",
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'StockWatch.wsgi.application'


# TODO
# if LIVE:
    # RAVEN_CONFIG = {
    #     'dsn': 'https://e9dedecf18764f1392e959d1badcfa38:5a57928068164499befd72e7bfb78492@sentry.io/1277127',
    #     'release': os.getenv('HEROKU_SLUG_COMMIT', '-'),
    # }


if LIVE:
    import dj_database_url
    DATABASES = {'default': dj_database_url.config()}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'stockwatch',
            'USER': os.getenv('PGUSER', 'postgres'),
            'PASSWORD': os.getenv('PGPASSWORD', 'waffle'),
            'HOST': os.getenv('PGHOST', 'localhost'),
            'PORT': os.getenv('PGPORT', '5432'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

try:
    from localsettings import *  # noqa
except ImportError:
    pass
