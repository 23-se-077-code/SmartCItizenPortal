from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-npkk#df1f57zlpgl6mx=09egw%bt!@s+^@t(#nz5@xd&_ar79-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ✅ FIXED: Allow Vercel domains
ALLOWED_HOSTS = ['.vercel.app', 'localhost', '127.0.0.1']

# Application definition
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
    'whitenoise.runserver_nostatic',  # ✅ ADDED: For static files on Vercel
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ ADDED: For static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smart_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # ✅ FIXED: Correct path
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

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Logging
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ✅ FIXED: Static files (for Vercel)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # ✅ ADDED

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URL
LOGIN_URL = '/users/login/'