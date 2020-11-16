import os

from sentry_sdk.integrations.django import DjangoIntegration

DJ_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(DJ_DIR)

SECRET_KEY = os.getenv('SECRET_KEY', '4d2a5e6514c95192aacab316ef5c0706')

DEBUG = os.getenv('DEBUG', True)
LIVE = os.getenv('LIVE')

ALLOWED_HOSTS = ['sorom.herokuapp.com', 'localhost']

VANTAGE_API_KEY = os.getenv('VANTAGE_API_KEY', '73KB3IKLT977N1M6')
QUANDL_API_KEY = os.getenv('QUANDL_API_KEY', '')
EOD_HD_API_KEY = os.getenv('EOD_HD_API_KEY', '')

AUTH_USER_MODEL = 'main.User'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'StockWatch.staticfiles',
    'django.contrib.staticfiles',
    'django_jinja',
    'django_extensions',
    'storages',
    'bootstrap3_datetime',
    'bootstrapform_jinja',
    'debug_toolbar',
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
    'StockWatch.main.middleware.AuthRequiredMiddleware',
]

ROOT_URLCONF = 'StockWatch.urls'

_TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',
    'django.template.context_processors.request',
    'django.template.context_processors.csrf',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'DIRS': ['templates'],
        'OPTIONS': {'match_extension': '.jinja', 'context_processors': _TEMPLATE_CONTEXT_PROCESSORS},
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': _TEMPLATE_CONTEXT_PROCESSORS},
    },
]

WSGI_APPLICATION = 'StockWatch.wsgi.application'


if LIVE:
    import sentry_sdk

    sentry_sdk.init(
        dsn='https://3b1874b64f8040a089e11e5c1133ae05@sentry.io/1453420', integrations=[DjangoIntegration()]
    )


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
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_ROOT = 'staticfiles'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_URL = '/static/'

if LIVE:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = 'salsa-verde'
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_STATIC_LOCATION = 'static'
else:
    MEDIA_ROOT = 'mediafiles'
    MEDIA_URL = '/media/'
    PUBLIC_URL = '/media/public/'


PRIVATE_FILE_STORAGE = 'main.storage_backends.PrivateMediaStorage'


try:
    from localsettings import *  # noqa
except ImportError:
    pass
