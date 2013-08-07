import os

ROOT_PROJECT = "%s/../../" % os.getcwd()

DEBUG = True
TEMPLATE_DEBUG = DEBUG
LOGIN_REDIRECT_URL = '/'

ADMINS = (
    ('None', 'nomail@xxxxxyyyyy.eu'),
)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'zython.sql',                      # Or path to database file if using sqlite3.
    }
}


MEDIA_URL = 'http://127.0.0.1/medias/'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
INTERNAL_IPS = ('127.0.0.1',)
INTERCEPT_REDIRECTS = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '%scache' % ROOT_PROJECT,
    }
}
