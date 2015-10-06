"""Django settings for example project."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production

SECRET_KEY = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

DEBUG = True

TEMPLATE_DEBUG = True


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'example.urls'

STATIC_URL = '/static/'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'example', 'templates')]

WSGI_APPLICATION = 'example.wsgi.application'


# Cache and database

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'example', 'db.sqlite3'),
    }
}

# To use another database, set the DJANGO_DATABASE_ENGINE environment variable.
if os.environ.get('DJANGO_DATABASE_ENGINE', '').lower() == 'postgresql':
    # % su postgres
    # % createuser debug_toolbar
    # % createdb debug_toolbar -O debug_toolbar
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'debug_toolbar',
            'USER': 'debug_toolbar',
        }
    }
if os.environ.get('DJANGO_DATABASE_ENGINE', '').lower() == 'mysql':
    # % mysql
    # mysql> CREATE DATABASE debug_toolbar;
    # mysql> GRANT ALL PRIVILEGES ON debug_toolbar.* TO 'debug_toolbar'@'localhost';
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'debug_toolbar',
            'USER': 'debug_toolbar',
        }
    }


# django-debug-toolbar

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'example', 'static')]
