"""
Django settings for WhatsappAvitoDjango project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import logging.config
from logging.handlers import TimedRotatingFileHandler
import os
import sys
from datetime import datetime

from pathlib import Path

from django.contrib import staticfiles
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# SECRET_KEY = 'django-insecure-5^^u7zy^#wd=$&7a3e3tmk0pj-j88t932m!dp2ayx1*cb$&0ix'
#
# DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "mainapp.apps.MainappConfig"
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

ROOT_URLCONF = 'WhatsappAvitoDjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'mainapp/templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'mainapp.context_processors.user_context_processor',

            ],
        },
    },
]

WSGI_APPLICATION = 'WhatsappAvitoDjango.wsgi.application'
ASGI_APPLICATION = 'WhatsappAvitoDjango.asgi.application'



# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Yekaterinburg'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'mainapp/static'),
]


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MEDIA_ROOT указывает на директорию, в которой будут храниться загружаемые файлы
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# MEDIA_URL используется для генерации URL-адресов для доступа к загружаемым файлам
MEDIA_URL = '/media/'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/accounts/'
LOGOUT_REDIRECT_URL = '/login/'

# Время жизни сессии в секундах (7 дней = 604800 секунд)
SESSION_COOKIE_AGE = 604800

# Автоматически обновлять время сессии при каждом запросе (по желанию)
SESSION_SAVE_EVERY_REQUEST = True

if DEBUG is True:
    WEBHOOK_API = os.getenv('WEBHOOK_API_DEV')
else:
    WEBHOOK_API = os.getenv('WEBHOOK_API')
OPENAI_KEY = os.getenv('OPENAI_KEY')

# Ensure the logs directory exists
log_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


# Define a function to generate log filename with current date
def get_log_filename():
    current_time = datetime.now()  # This will use the server's local time
    return os.path.join(log_dir, f'debug_{current_time.strftime("%Y-%m-%d")}.log')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': get_log_filename(),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'openai': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
# LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
#
# # Исключаем логи опроса OpenAI
# class NoHttpCoreOpenAIFilter(logging.Filter):
#     def filter(self, record):
#         return not (
#             record.name.startswith("httpcore") or
#             record.name.startswith("httpx") or
#             record.name.startswith("openai")
#         )
#
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {pathname} {lineno} {module} {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{levelname} {message}',
#             'style': '{',
#         },
#     },
#     'filters': {
#         'exclude_httpcore_openai': {
#             '()': NoHttpCoreOpenAIFilter,
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': LOG_LEVEL,
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose',
#             'filters': ['exclude_httpcore_openai'],
#         },
#         'file': {
#             'level': LOG_LEVEL,
#             'class': 'logging.handlers.TimedRotatingFileHandler',
#             'filename': os.path.join(BASE_DIR, 'logs', 'app.log'),
#             'when': 'midnight',
#             'backupCount': 7,
#             'formatter': 'verbose',
#             'filters': ['exclude_httpcore_openai'],
#         },
#     },
#     'root': {
#         'handlers': ['console', 'file'],
#         'level': 'DEBUG',
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console', 'file'],
#             'level': DJANGO_LOG_LEVEL,
#             'propagate': True,
#         },
#         'django.request': {
#             'handlers': ['console', 'file'],
#             'level': DJANGO_LOG_LEVEL,
#             'propagate': False,
#         },
#         'django.db.backends': {
#             'handlers': ['console', 'file'],
#             'level': DJANGO_LOG_LEVEL,
#             'propagate': False,
#         },
#         'django.utils.autoreload': {
#             'handlers': ['console', 'file'],
#             'level': 'WARNING',
#             'propagate': False,
#         },
#         'myapp': {
#             'handlers': ['console', 'file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }
#
# # Применяем настройки логирования
# logging.config.dictConfig(LOGGING)
