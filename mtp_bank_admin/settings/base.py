"""
Django settings for mtp_bank_admin project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
from functools import partial
import os
from os.path import abspath, dirname, join
import sys

BASE_DIR = dirname(dirname(abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

get_project_dir = partial(join, BASE_DIR)

APP = 'bank-admin'
ENVIRONMENT = os.environ.get('ENV', 'local')
APP_BUILD_DATE = os.environ.get('APP_BUILD_DATE')
APP_GIT_COMMIT = os.environ.get('APP_GIT_COMMIT')
MOJ_INTERNAL_SITE = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SECRET_KEY = 'CHANGE_ME'
ALLOWED_HOSTS = []

START_PAGE_URL = os.environ.get('START_PAGE_URL', 'https://www.gov.uk/send-prisoner-money')
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8002')

# Application definition
INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.auth',
)
PROJECT_APPS = (
    'anymail',
    'mtp_common',
    'widget_tweaks',
    'bank_admin',
    'zendesk_tickets'
)
INSTALLED_APPS += PROJECT_APPS


WSGI_APPLICATION = 'mtp_bank_admin.wsgi.application'
ROOT_URLCONF = 'mtp_bank_admin.urls'
MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'mtp_common.auth.csrf.CsrfViewMiddleware',
    'mtp_common.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

HEALTHCHECKS = []
AUTODISCOVER_HEALTHCHECKS = True

# security tightening
# some overridden in prod/docker settings where SSL is ensured
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False
CSRF_FAILURE_VIEW = 'mtp_common.auth.csrf.csrf_failure'


# Data stores
DATABASES = {}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mtp',
    }
}


# Internationalization
LANGUAGE_CODE = 'en-gb'
LANGUAGES = (
    ('en-gb', 'English'),
    ('cy', 'Cymraeg'),
)
LOCALE_PATHS = (get_project_dir('translations'),)
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_ROOT = 'static'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    get_project_dir('assets'),
    get_project_dir('assets-static'),
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            get_project_dir('templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'mtp_common.context_processors.analytics',
                'mtp_common.context_processors.app_environment',
                'bank_admin.context_processors.govuk_localisation',
            ],
        },
    },
]

# logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
        'elk': {
            '()': 'mtp_common.logging.ELKFormatter'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple' if ENVIRONMENT == 'local' else 'elk',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['console'],
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'mtp': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# sentry exception handling
if os.environ.get('SENTRY_DSN'):
    INSTALLED_APPS = ('raven.contrib.django.raven_compat',) + INSTALLED_APPS
    RAVEN_CONFIG = {
        'dsn': os.environ['SENTRY_DSN'],
        'release': APP_GIT_COMMIT or 'unknown',
    }
    LOGGING['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler'
    }
    LOGGING['root']['handlers'].append('sentry')
    LOGGING['loggers']['mtp']['handlers'].append('sentry')

TEST_RUNNER = 'mtp_common.test_utils.runner.TestRunner'

# authentication
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

AUTHENTICATION_BACKENDS = (
    'mtp_common.auth.backends.MojBackend',
)


def find_api_url():
    import socket
    import subprocess

    api_port = int(os.environ.get('API_PORT', '8000'))
    try:
        host_machine_ip = subprocess.check_output(['docker-machine', 'ip', 'default'],
                                                  stderr=subprocess.DEVNULL)
        host_machine_ip = host_machine_ip.decode('ascii').strip()
        with socket.socket() as sock:
            sock.connect((host_machine_ip, api_port))
    except (subprocess.CalledProcessError, OSError):
        host_machine_ip = 'localhost'
    return 'http://%s:%s' % (host_machine_ip, api_port)


# control the time a session exists for; should match api's access token expiry
SESSION_COOKIE_AGE = 60 * 60  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True


API_CLIENT_ID = 'bank-admin'
API_CLIENT_SECRET = os.environ.get('API_CLIENT_SECRET', 'bank-admin')
API_URL = os.environ.get('API_URL', find_api_url())

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'bank_admin:dashboard'
LOGOUT_URL = 'logout'

OAUTHLIB_INSECURE_TRANSPORT = True


GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', None)

REFUND_REFERENCE = 'Refund %s %s'
REFUND_OUTPUT_FILENAME = 'mtp_accesspay_{date:%d%m%y}.txt'

ADI_TEMPLATE_FILEPATH = 'local_files/adi_template.xlsm'
ADI_CACHED_OUTPUT_FILENAME = 'adi_journal_{date:%d%m%Y}_MTP01.xlsm'
ADI_OUTPUT_FILENAME = '0210_SSCL_{initials}_{date:%d%m%Y}_MTP01.xlsm'

BANK_STMT_ACCOUNT_NUMBER = os.environ.get('BANK_STMT_ACCOUNT_NUMBER', '')
BANK_STMT_SORT_CODE = os.environ.get('BANK_STMT_SORT_CODE', '')
BANK_STMT_CURRENCY = os.environ.get('BANK_STMT_CURRENCY', 'GBP')
BANK_STMT_OUTPUT_FILENAME = 'NMS{account_number}{date:%d%m%Y}.dat'

DISBURSEMENT_TEMPLATE_FILEPATH = 'local_files/disbursement_template.xlsm'
DISBURSEMENT_OUTPUT_FILENAME = 'mtp_disbursements_{date:%d%m%Y}.xlsm'

REQUEST_PAGE_SIZE = 500

ZENDESK_BASE_URL = 'https://ministryofjustice.zendesk.com'
ZENDESK_API_USERNAME = os.environ.get('ZENDESK_API_USERNAME', '')
ZENDESK_API_TOKEN = os.environ.get('ZENDESK_API_TOKEN', '')
ZENDESK_REQUESTER_ID = os.environ.get('ZENDESK_REQUESTER_ID', '')
ZENDESK_GROUP_ID = 26417927
ZENDESK_CUSTOM_FIELDS = {
    'referer': 26047167,
    'username': 29241738,
    'user_agent': 23791776,
    'contact_email': 30769508,
}

EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
ANYMAIL = {
    'MAILGUN_API_KEY': os.environ.get('MAILGUN_ACCESS_KEY', ''),
    'MAILGUN_SENDER_DOMAIN': os.environ.get('MAILGUN_SERVER_NAME', ''),
    'SEND_DEFAULTS': {
        'tags': [APP, ENVIRONMENT],
    },
}
MAILGUN_FROM_ADDRESS = os.environ.get('MAILGUN_FROM_ADDRESS', '')
if MAILGUN_FROM_ADDRESS:
    DEFAULT_FROM_EMAIL = MAILGUN_FROM_ADDRESS

SHOW_LANGUAGE_SWITCH = os.environ.get('SHOW_LANGUAGE_SWITCH', 'False') == 'True'

BANK_ADMIN_USERNAME = os.environ.get('BANK_ADMIN_USERNAME', 'refund-bank-admin')
BANK_ADMIN_PASSWORD = os.environ.get('BANK_ADMIN_PASSWORD', 'refund-bank-admin')

try:
    from .local import *  # noqa
except ImportError:
    pass
