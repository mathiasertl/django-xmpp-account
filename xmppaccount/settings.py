# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:hlsearch
#
# This file is part of django-xmpp-account (https://github.com/mathiasertl/django-xmpp-account/).
#
# django-xmpp-account is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# django-xmpp-account is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with django-xmpp-account.
# If not, see <http://www.gnu.org/licenses/>.

import glob
import gnupg
import logging
import os

from datetime import timedelta
log = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '.xmppaccount.sqlite3',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Vienna'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# add request preprocessor to default
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "core.context_processors.xmppaccount",
)

MIDDLEWARE_CLASSES = (
    'core.middleware.SiteMiddleware',
    'core.middleware.AntiSpamMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'xmppaccount.urls'

# always upload to temporary files right away, since gnupg needs files there
FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.TemporaryFileUploadHandler",)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'xmppaccount.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    'captcha',

    'core',
    'register',
    'reset',
    'delete',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

AUTHENTICATION_BACKENDS = (
    'core.auth_backends.BackendBackend',
)

AUTH_USER_MODEL = 'core.RegistrationUser'

# custom settings defaults
XMPP_HOSTS = {}
XMPP_HOSTS_MAPPING = {}
DEFAULT_XMPP_HOST = None
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 32

CLEARTEXT_PASSWORDS = True
CONFIRMATION_TIMEOUT = timedelta(hours=24)
FORM_TIMEOUT = 60 * 60  # 1 hour

SPAM_BLOCK_TIME = 60 * 60 * 24  # one day!
REGISTRATION_RATE = {
    timedelta(minutes=2): 1,
    timedelta(hours=1): 2,
    timedelta(days=1): 5,
}
BLOCKED_EMAIL_TLDS = set()

BRAND = ""
CONTACT_URL = ""
WELCOME_MESSAGE = None

# logging
LOGDIR = os.path.join(BASE_DIR, 'logs')
LOG_LEVEL = 'WARNING'
RATELIMIT_WHITELIST = set()

# Captchas
CAPTCHA_LENGTH = 8
CAPTCHA_FONT_SIZE = 32

# GPG config
GNUPG = {
    'gnupghome': os.path.join(BASE_DIR, '.gpg'),
    'gpgbinary': '/usr/bin/gpg',
    'options': ['--lock-multiple'],
}
GPG_KEYSERVER = 'pool.sks-keyservers.net'
FORCE_GPG_SIGNING = False

# Celery configuration
BROKER_URL = None
CELERY_RESULT_BACKEND = None
CELERY_ACCEPT_CONTENT = ['json']

try:
    from xmppaccount.localsettings import *
except ImportError as e:
    print(e)
    pass

MANAGED_HOSTS = [k for k, v in XMPP_HOSTS.items() if v.get('MANAGE', True)]
RESERVATION_HOSTS = [k for k, v in XMPP_HOSTS.items()
                     if v.get('RESERVATION') and v.get('MANAGE', True)]
REGISTRATION_HOSTS = [k for k, v in XMPP_HOSTS.items()
                      if v.get('REGISTRATION') and v.get('MANAGE', True)]
NO_EMAIL_HOSTS = [k for k, v in XMPP_HOSTS.items() if not v.get('EMAIL')]
BLOCKED_EMAIL_TLDS.update(NO_EMAIL_HOSTS)

if MAX_USERNAME_LENGTH > 255:
    MAX_USERNAME_LENGTH = 255

if DEFAULT_XMPP_HOST is None:
    DEFAULT_XMPP_HOST = list(XMPP_HOSTS.values())[0]

GPG = None
if GNUPG is not None:
    if os.path.exists(GNUPG['gnupghome']):
        GPG = gnupg.GPG(**GNUPG)
    else:
        log.warn('GnuPG disabled because GnuPG home not found. Generate key with manage.py genkey.')

if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)

# compute path to latest minified js/css files
_static_base = os.path.join(BASE_DIR, 'core', 'static')
MINIFIED_JS = sorted(glob.glob(os.path.join(_static_base, 'account-*.min.js')))[-1]
MINIFIED_JS = '%s%s' % (STATIC_URL, os.path.basename(MINIFIED_JS))
MINIFIED_CSS = sorted(glob.glob(os.path.join(_static_base, 'account-*.min.css')))[-1]
MINIFIED_CSS = '%s%s' % (STATIC_URL, os.path.basename(MINIFIED_CSS))

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime).19s %(levelname)-8s] %(message)s',  # .19s = only first 19 chars
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'cron-console': {  # always log error to stdout
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'cleanup': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGDIR, 'cleanup.log'),
            'formatter': 'simple',
        },
        'import': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGDIR, 'import.log'),
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'backends': {
            'handlers': ['console', ],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'core': {
            'handlers': ['console', ],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'register': {
            'handlers': ['console', ],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'reset': {
            'handlers': ['console', ],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'delete': {
            'handlers': ['console', ],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'cleanup': {
            'handlers': ['cleanup', 'cron-console'],
            'level': LOG_LEVEL,
        },
        'import': {
            'handlers': ['import', 'cron-console'],
            'level': LOG_LEVEL,
        },
    },
}
