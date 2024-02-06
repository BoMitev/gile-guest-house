import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', default=False)

ALLOWED_HOSTS = ['*']

SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', default=False)
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', default=False)

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
]

THIRD_PARTY_APPS = [
    'admin_extra_buttons',
    'simple_history',
    'rest_framework',
]

GILE_APPS = [
    "hotel_gile.main_app",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + GILE_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'hotel_gile.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'hotel_gile.wsgi.application'

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE')
TIME_ZONE = os.getenv('TIME_ZONE')
USE_I18N = os.getenv('USE_I18N')
USE_TZ = os.getenv('USE_TZ')

# USE_L10N = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DATE_INPUT_FORMATS = ('%d.%m.%Y', '%Y-%m-%d', '%Y-%m-%d',)
DATETIME_FORMAT = "d.m.Y H:i:s"
ADMIN_LIST_DISPLAY_DATETIME_FORMAT = "%d %b %Y %H:%M"
ADMIN_LIST_DISPLAY_DATE_FORMAT = "%d %b %Y"

CURRENCY_DISPLAY = os.getenv('CURRENCY_DISPLAY')
CURRENCY = os.getenv('CURRENCY')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = 25
ALTERNATIVE_USER = os.getenv('ALTERNATIVE_USER')
EMAIL_SRVC_ENDPOINT = os.getenv('EMAIL_SRVC_ENDPOINT')

# Tuya Locker
TUYA_ACCESS_ID = os.getenv('TUYA_ACCESS_ID')
TUYA_ACCESS_KEY = os.getenv('TUYA_ACCESS_KEY')
TUYA_API_ENDPOINT = os.getenv('TUYA_API_ENDPOINT')
TUYA_DEVICE_ID = os.getenv('TUYA_DEVICE_ID')

# Google APi
GOOGLE_CLIENT_SECRET_FILE = os.getenv('GOOGLE_CLIENT_SECRET_FILE')
GOOGLE_API_NAME = os.getenv('GOOGLE_API_NAME')
GOOGLE_API_VERSION = os.getenv('GOOGLE_API_VERSION')
GOOGLE_SCOPES = ['https://mail.google.com/']

# Reviews APi
REVIEW_API_URL = os.getenv('REVIEW_API_URL')
REVIEW_QUERYSTRING = {
    "hotel_id": os.getenv('REVIEW_HOTEL_ID'),
    "locale": os.getenv('REVIEW_LOCALE'),
    "sort_type": os.getenv('REVIEW_SORT_TYPE')
}
REVIEW_HEADERS = {
    "X-RapidAPI-Key": os.getenv('REVIEW_API_KEY'),
    "X-RapidAPI-Host": os.getenv('REVIEW_HOST')
}