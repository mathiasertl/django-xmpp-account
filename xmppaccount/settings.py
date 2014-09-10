# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-register (https://account.jabber.at/doc).
#
# django-xmpp-register is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# django-xmpp-register is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-register.  If not, see <http://www.gnu.org/licenses/>.

import os

from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG
RECAPTCHA_CLIENT = None
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

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
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'igw!e%gbu_u+e%+$*d3u_(lo#ixs2pqrv@9zzzw(mpkx6q9qm+'

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
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

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

RECAPTCHA_PRIVATE_KEY = None
RECAPTCHA_PUBLIC_KEY = None
BRAND = ""
CONTACT_URL = ""
WELCOME_MESSAGE = None

try:
    from localsettings import *
except ImportError:
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
    DEFAULT_XMPP_HOST = XMPP_HOSTS.values()[0]

if RECAPTCHA_PRIVATE_KEY and RECAPTCHA_PUBLIC_KEY:
    from recaptcha import RecaptchaClient
    RECAPTCHA_CLIENT = RecaptchaClient(RECAPTCHA_PRIVATE_KEY, RECAPTCHA_PUBLIC_KEY)

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
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
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
            'level': 'DEBUG',
        },
    }
}
