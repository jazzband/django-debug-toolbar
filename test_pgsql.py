from django.conf import global_settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # Edit the below settings before use...
        'USER': '',
        'NAME': '',
        'HOST': '',
        'PASSWORD': '',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'debug_toolbar',

    'tests',
]

MIDDLEWARE_CLASSES = global_settings.MIDDLEWARE_CLASSES + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = ''

DEBUG = False

SITE_ID = 1
