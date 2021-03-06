"""
Django settings for document_searcher project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$ie8@7sx#m)ft8n+9-&(gv5_9^syfci7^#xqab+u6t#t-&+ykt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'doc_search',
    'haystack',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'document_searcher.urls'

WSGI_APPLICATION = 'document_searcher.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'document_searcher',
        'USER': 'document_searcher',
        'PASSWORD': 'document_searcher',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Haystack

if DEBUG:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
        },
    }

else:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'haystack',
            'TIMEOUT': 3600,
        },
    }

ALLOWED_HOSTS = ['.com']

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'templates').replace('\\','/'),
    os.path.join(BASE_DIR, 'document_searcher', 'templates').replace('\\', '/'),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

LOGGER_NAME = 'document_puller.logger'

if not DEBUG:
    ROOT_FILE_DIR = '/home/ec2-user/files'
    ROOT_TXT_DIR = '/home/ec2-user/txtfiles'
    ROOT_NEW_DIR = '/home/ec2-user/newfiles'
    LOG_FILE = '/home/ec2-user/document_puller.log'
    REQUEST_LOG_FILE = '/home/ec2-user/document_puller_request.log'
    NEW_FILE_INCREMENT = 1000
else:
    ROOT_FILE_DIR = '/Users/ruven/Documents/documents/files'
    ROOT_TXT_DIR = '/Users/ruven/Documents/documents/textfiles'
    ROOT_NEW_DIR = '/Users/ruven/Documents/documents/newfiles'
    LOG_FILE = '/Users/ruven/Documents/documents/document_puller.log'
    REQUEST_LOG_FILE = '/Users/ruven/Documents/documents/document_puller_request.log'
    NEW_FILE_INCREMENT = 50

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'standard': {
            'format': '%(asctime)s %(message)s'
        },
    },
    'handlers': {
        'request_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': REQUEST_LOG_FILE,
        },
        'file' : {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'standard',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['request_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        LOGGER_NAME: {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate' : True,
        },
    },
}
