import os
import sys
import codecs
from pathlib import Path
from environ import Env
from datetime import timedelta

from apps import users

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env.str('SECRET_KEY', 'unsafe-default-secret-key')


DEBUG = env.bool("DEBUG", False)
if DEBUG:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
else:
    ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")



INSTALLED_APPS = [

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",


    # Third-party packages
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "rest_framework_simplejwt",
     "djmoney",
    "simple_history",
    "rest_framework_simplejwt.token_blacklist",


    # Local project applications
    "apps.core.apps.CoreConfig",
    "apps.users.apps.UsersConfig",
    "apps.listings.apps.ListingsConfig",
    "apps.reservations.apps.ReservationsConfig",
    "apps.reviews.apps.ReviewsConfig",
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    "simple_history.middleware.HistoryRequestMiddleware",
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


if env.bool('MYSQL'):
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': env.str('DB_NAME'),
          'USER': env.str('DB_USER'),
          'PASSWORD': env.str('DB_PASSWORD'),
          'HOST': env.str('DB_HOST'),
          'PORT': env.str('DB_PORT'),
      },
      'test': {'NAME': f"test_{env.str('DB_NAME')}"},
  }
else:
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': BASE_DIR / 'db.sqlite3',
      }
  }




AUTH_USER_MODEL = 'users.User'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]





REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 3,
    'PAGE_QUERY_PARAM': 'page',
    'PAGE_SIZE_QUERY_PARAM': 'page_size',
    'MAX_PAGE_SIZE': 100,

    'DEFAULT_PARSER_CLASSES': [
            'rest_framework.parsers.JSONParser',
        ],


    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',



    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework_simplejwt.authentication.JWTAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
        'apps.users.authentication.CookieJWTAuthentication',

    ),
    'DEFAULT_PERMISSION_CLASSES': [
        #'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        #'rest_framework.permissions.IsAuthenticated',
    ],

     'DEFAULT_THROTTLE_CLASSES': [
       # 'rest_framework.throttling.AnonRateThrottle',
       #   'rest_framework.throttling.UserRateThrottle',
    ],
     'DEFAULT_THROTTLE_RATES': {
         'anon': '2/day',
         'user': '7/day',
    },
}

# SimpleJWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# =========================
# EMAIL - LOCAL DEVELOPMENT
# =========================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'webmaster@Django_DAMASHKI.local'


# =========================
# EMAIL - PRODUCTION / SERVER
# =========================
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your_email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your_app_password'
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER



LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True



STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': codecs.getwriter('utf-8')(sys.stdout.buffer),
            'formatter': 'simple',
        },
        'http_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'http_logs.log',
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 3,
            'backupCount': 2,
            'encoding': 'utf-8',
            'delay': True,
        },
        'db_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'db_logs.log',
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 3,
            'backupCount': 2,
            'encoding': 'utf-8',
            'delay': True,
        },
    },
    'loggers': {
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['http_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['http_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['db_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# 2. SPECTACULAR_SETTINGS

SPECTACULAR_SETTINGS = {
    "TITLE": "Rentify API",
    "VERSION": "1.0.0",
    "DESCRIPTION": "Real Estate Listing and Booking Platform API",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "GET_LIB_DOCSTRINGS": True,
}