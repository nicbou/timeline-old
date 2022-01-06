import logging.config
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/api/static/'
MEDIA_ROOT = '/'
MEDIA_URL = '/'

DATA_ROOT = Path('/data')  # Files that are included in backups
ASSETS_ROOT = Path('/assets')  # Files that can be regenerated, and don't need to be backed up

ARCHIVES_ROOT = DATA_ROOT / 'archives'
BACKUPS_ROOT = DATA_ROOT / 'backups'
MOUNTS_ROOT = DATA_ROOT / 'mounts'
PREVIEWS_ROOT = ASSETS_ROOT / 'previews'
STATIC_ROOT = ASSETS_ROOT / 'static'
ENTRIES_DUMP_PATH = DATA_ROOT / 'all-entries.json'

SSH_DIR = Path('/root/.ssh')
TIMELINE_INCLUDE_FILE = '.timelineinclude'


# Ensure that the absolute URLs in API responses are correct, even behind the reverse proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('BACKEND_SECRET_KEY', False)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('BACKEND_DEBUG', False) == '1'
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'rest_framework',
    'generic_relations',
    'timeline.apps.TimelineConfig',
    'archive.apps.ArchiveConfig',
    'backup.apps.BackupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'timeline',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'timeline-db',
        'PORT': 5432,
    }
}

# Logging
LOGGING_CONFIG = None
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            "()": "coloredlogs.ColoredFormatter",
            'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'gunicorn.access': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': True,
            'qualname': 'gunicorn.access',
        },
        'pydriller': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': True,
        }
    },
})


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

IMAGE_PREVIEW_SIZES = {
    'thumbnail': {
        'width': 1200,
        'height': 200,
    },
    'thumbnail2x': {
        'width': 2400,
        'height': 400,
    },
    'preview': {
        'width': 1800,
        'height': 1200,
    },
    'preview2x': {
        'width': 3600,
        'height': 2400,
    },
}

DOCUMENT_PREVIEW_SIZES = {
    'thumbnail': {
        'width': 1200,
        'height': 200,
    },
    'thumbnail2x': {
        'width': 2400,
        'height': 400,
    },
    'preview': {
        'width': 1800,
        'height': 1800,
    },
    'preview2x': {
        'width': 3600,
        'height': 3600,
    },
}

VIDEO_PREVIEW_SIZES = {
    'thumbnail': {
        'width': 400,
        'height': 200,
    },
    'preview': {
        'width': 1280,
        'height': 720,
    },
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination'
}

# In bytes
MAX_PLAINTEXT_PREVIEW_SIZE = 10000  # 2KB = 1 page of text


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = True
