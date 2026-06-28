from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-npkk#df1f57zlpgl6mx=09egw%bt!@s+^@t(#nz5@xd&_ar79-'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'cnic',
    'passport',
    'complaints',
    'voting',
    'challan',
    'citizens',
    'formtools',
    
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

ROOT_URLCONF = 'smart_portal.urls'

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # changed  # IMPORTANT FIX
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

WSGI_APPLICATION = 'smart_portal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'cnic.views': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# JazzCash
JAZZCASH_MERCHANT_ID = "YOUR_MERCHANT_ID"
JAZZCASH_PASSWORD = "YOUR_PASSWORD"
JAZZCASH_INTEGRITY_SALT = "YOUR_INTEGRITY_SALT"
JAZZCASH_RETURN_URL = "https://yourdomain.com/challan/jazzcash-return/"
JAZZCASH_SANDBOX_URL = "https://sandbox.jazzcash.com.pk/ApplicationAPI/API/Payment/DoPayment"
JAZZCASH_LIVE_URL = "https://payments.jazzcash.com.pk/ApplicationAPI/API/Payment/DoPayment"

# EasyPaisa
EASYPAISA_MERCHANT_ID = "YOUR_MERCHANT_ID"
EASYPAISA_PASSWORD = "YOUR_PASSWORD"
EASYPAISA_RETURN_URL = "https://yourdomain.com/challan/easypaisa-return/"
EASYPAISA_SANDBOX_URL = "https://easypaystg.easypaisa.com.pk/easypay-service/rest/v4/..."
EASYPAISA_LIVE_URL = "https://easypay.easypaisa.com.pk/easypay-service/rest/v4/..."

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/users/login/'
