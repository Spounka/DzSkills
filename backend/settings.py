import os.path
import socket
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

if not os.path.isfile(BASE_DIR / '.env'):
    raise RuntimeError('No dotenv found, please create one')

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY', '')

# DOCKER_SETTINGS
DEBUG = (os.environ.get('DEBUG', True) == "true")
# DEBUG = True

# DOCKER_SETTINGS
ALLOWED_HOSTS = ['*']

# Application definition

# DOCKER_SETTINGS
CSRF_TRUSTED_ORIGINS = [
    "https://dzskills.fly.dev",
    'http://localhost:3000',
    'http://localhost',
    'http://localhost:8000',
    "https://dzskills.vercel.app",
]

# DOCKER_SETTINGS
# CORS_ALLOWED_ORIGINS = [
#     'http://localhost',
#     'http://localhost:3000',
#     'http://localhost:4173',
#     "https://dzskills.fly.dev",
#     "https://dzskills.vercel.app",
# ]

# DOCKER_SETTINGS
CORS_ALLOW_ALL_ORIGINS = True

# DOCKER_SETTINGS
HOSTNAME = 'localhost'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'corsheaders',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Rest framework
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',

    # All Auth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',

    # My Apps
    'authentication',
    'user_profile',
    'admin_dashboard',

    'student',
    'courses',
    'course_buying',
    'comment',
    'messaging',
    'support',

    # Social Accounts
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
]

# DOCKER_SETTINGS
SITE_ID = 1

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        },
        'OAUTH_PKCE_ENABLED': True,
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'en_US',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v16.0',
        'GRAPH_API_URL': 'https://graph.facebook.com/v17.0',
    }
}

SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_ADAPTER = 'authentication.adapter.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'authentication.adapter.SocialAdapter'

# DOCKER_SETTINGS
EMAIL_ACTIVATION_URL = '/register/verify-email/'

ACCOUNT_EMAIL_VERIFICATION = 'optional'
REST_AUTH_REGISTER_VERIFICATION_ENABLED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
SOCIALACCOUNT_STORE_TOKENS = True

# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'boudaakkarnazih@gmail.com'
# EMAIL_HOST_PASSWORD = 'xfbdmgszftyvycsr'
#

EMAIL_HOST = 'smtp.titan.email'
EMAIL_HOST_USER = 'no-reply@dzskills.com'
EMAIL_HOST_PASSWORD = 'DZskills2023@'
EMAIL_PORT = 465
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_SSL = True

ADMIN_EMAIL = "no-reply@dzskills.com"
SUPPORT_EMAIL = "no-reply@dzskills.com"
DEFAULT_FROM_EMAIL = ADMIN_EMAIL
SERVER_EMAIL = ADMIN_EMAIL

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(weeks=4),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
}

REST_AUTH = {
    'USER_DETAILS_SERIALIZER': 'authentication.serializers.UserSerializer',
    'REGISTER_SERIALIZER': 'authentication.serializers.RegistrationSerializer',
    'SESSION_LOGIN': False,
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'dz-skills-token',
    'JWT_AUTH_REFRESH_COOKIE': 'dz-skills-refresh',
    'JWT_AUTH_HTTPONLY': False,
}

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]

}

AUTHENTICATION_BACKENDS = [
    # Needed to log in by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    'authentication.auths.AuthWithEmail',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# DOCKER SETTINGS
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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

# DOCKER_SETTINGS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', os.environ.get('DB', '')),
        'USER': os.environ.get('POSTGRES_USER', os.environ.get('DB_USER', '')),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', os.environ.get('DB_PASS', '')),
        'HOST': os.environ.get('POSTGRES_HOST', '172.20.0.2'),
        'PORT': 5432
    }

}

# DOCKER_SETTINGS
if os.environ.get('DATABASE_URL', None):
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])

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

LANGUAGE_CODE = 'ar-ar'

TIME_ZONE = 'Africa/Algiers'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = 'http://localhost/static/'
MEDIA_URL = 'http://localhost/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'authentication.User'

FILE_UPLOAD_MAX_MEMORY_SIZE = 1024
