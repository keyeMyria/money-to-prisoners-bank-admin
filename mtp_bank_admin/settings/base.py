"""
Django settings for mtp_bank_admin project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
from functools import partial
import json
import os
from os.path import abspath, dirname, join
import sys

BASE_DIR = dirname(dirname(abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

get_project_dir = partial(join, BASE_DIR)

APP = 'bank-admin'
ENVIRONMENT = os.environ.get('ENV', 'local')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SECRET_KEY = 'CHANGE_ME'
ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)
PROJECT_APPS = (
    'moj_utils',
    'widget_tweaks',
    'bank_admin',
    'zendesk_tickets'
)
INSTALLED_APPS += PROJECT_APPS


WSGI_APPLICATION = 'mtp_bank_admin.wsgi.application'
ROOT_URLCONF = 'mtp_bank_admin.urls'
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'moj_auth.csrf.CsrfViewMiddleware',
    'moj_auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)


# security tightening
# some overridden in prod/docker settings where SSL is ensured
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False
CSRF_FAILURE_VIEW = 'moj_auth.csrf.csrf_failure'


# Database
DATABASES = {}


# Internationalization
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_ROOT = 'static'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    get_project_dir('assets'),
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            get_project_dir('templates'),
            get_project_dir('node_modules'),
            get_project_dir('../node_modules/mojular-templates'),
            get_project_dir('../node_modules/money-to-prisoners-common/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'moj_utils.context_processors.analytics',
                'moj_utils.context_processors.app_environment',
            ],
        },
    },
]

# sentry exception handling
if os.environ.get('SENTRY_DSN'):
    INSTALLED_APPS = ('raven.contrib.django.raven_compat',) + INSTALLED_APPS
    RAVEN_CONFIG = {
        'dsn': os.environ['SENTRY_DSN'],
        'release': os.environ.get('APP_GIT_COMMIT', 'unknown'),
    }

# authentication
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

AUTHENTICATION_BACKENDS = (
    'moj_auth.backends.MojBackend',
)

API_CLIENT_ID = 'bank-admin'
API_CLIENT_SECRET = os.environ.get('API_CLIENT_SECRET', 'bank-admin')
API_URL = os.environ.get('API_URL', 'http://localhost:8000')

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'bank_admin:dashboard'
LOGOUT_URL = 'logout'

OAUTHLIB_INSECURE_TRANSPORT = True


GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', None)

REFUND_REFERENCE = 'Payment refunded'
REFUND_OUTPUT_FILENAME = 'mtp_accesspay_%d%m%y.csv'

ADI_TEMPLATE_FILEPATH = 'local_files/adi_template.xlsx'
ADI_PAYMENT_OUTPUT_FILENAME = 'adi_credit_file_%d%m%y.xlsx'
ADI_REFUND_OUTPUT_FILENAME = 'adi_refund_file_%d%m%y.xlsx'

BANK_STMT_SENDER_ID = os.environ.get('BANK_STMT_SENDER_ID', 'NWBKGB2L')
BANK_STMT_RECEIVER_ID = os.environ.get('BANK_STMT_RECEIVER_ID', '391796')
BANK_STMT_ACCOUNT_NUMBER = os.environ.get('BANK_STMT_ACCOUNT_NUMBER',
                                          '10002383 607080')
BANK_STMT_CURRENCY = os.environ.get('BANK_STMT_CURRENCY', 'GBP')
BANK_STMT_OUTPUT_FILENAME = 'stmt_%d%m%y'

REQUEST_PAGE_SIZE = 500

ZENDESK_BASE_URL = 'https://ministryofjustice.zendesk.com'
ZENDESK_API_USERNAME = os.environ.get('ZENDESK_API_USERNAME', '')
ZENDESK_API_TOKEN = os.environ.get('ZENDESK_API_TOKEN', '')
ZENDESK_REQUESTER_ID = os.environ.get('ZENDESK_REQUESTER_ID', '')
ZENDESK_GROUP_ID = 26417927
ZENDESK_CUSTOM_FIELDS = {
    'referer': 26047167,
    'username': 29241738,
    'user_agent': 23791776
}

try:
    from .local import *  # noqa
except ImportError:
    pass
