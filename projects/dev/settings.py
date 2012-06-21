 # -*- coding: utf-8 -*-
 # Django static settings
from local_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEFAULT_CHARSET = 'utf-8'
MANAGERS = ADMINS

TIME_ZONE = 'Europe/Paris'
DEFAULT_FROM_EMAIL = 'ToBeer <noreply@beer.martync.me>'

LANGUAGE_CODE = 'en'
LOCALE_PATHS = (
    "%slocale/" % ROOT_PROJECT,
)
LANGUAGES = (
    ('en', u'English'),
    ('fr', u'Français')
)

USE_I18N = True
USE_L10N = True
USE_TZ = True

SITE_ID = 1


MEDIA_ROOT = '%smedias/' % ROOT_PROJECT 
#ADMIN_MEDIA_PREFIX = '/media/'
STATIC_URL = "%sstatic/" % MEDIA_URL
STATIC_ROOT = '%sstatic/' % MEDIA_ROOT
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


ROOT_URLCONF = 'dev.urls'

SECRET_KEY = 'sa52(fruc7(4%hu!z2pi38a!om$nf$s+)6c^0hk=$ol@u3g7ji'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages', 
    'units.context_processors.user_units',
    'units.context_processors.unit_menu',
)



TEMPLATE_DIRS = (
    "%stemplates/" % ROOT_PROJECT,
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.comments', 
    'django.contrib.admin',
    'django.contrib.admindocs',

    'accounts', 
    'public',
    'brew',
    'units',

    'registration',
    'inspect_model',
    'avatar', 
    # 'debug_toolbar'
)

ACCOUNT_ACTIVATION_DAYS = 7
AVATAR_ALLOWED_FILE_EXTS = ('.jpg', '.png', '.jpeg', '.gif')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}