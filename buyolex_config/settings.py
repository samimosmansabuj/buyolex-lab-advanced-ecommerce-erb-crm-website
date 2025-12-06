from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
import os
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv('DEBUG', 'False').strip().lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
# CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False").strip().lower() in ('true', '1', 'yes')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework', 'rest_framework_simplejwt',
    'corsheaders', 'django_extensions', 'django_filters',
    'rest_framework_simplejwt.token_blacklist',
    'django_htmx',

    'accounts', 'analytics', 'api', 'catalog', 'landing_pages', 'marketing', 'offers', 'orders', 'settings_app', 'dashboard'
]


# ================================================================================
# ==================== Rest Frame Work Configurations Start====================
ENABLE_BROWSABLE_API = os.getenv('ENABLE_BROWSABLE_API', 'False') == 'True'
if ENABLE_BROWSABLE_API:
    DEFAULT_RENDERER_CLASSES_ = [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
else:
    DEFAULT_RENDERER_CLASSES_ = [
        'rest_framework.renderers.JSONRenderer'
    ]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES_,
    
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    
    # 'EXCEPTION_HANDLER': 'authentication.utils.custom_exception_handler',
    
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'PAGE_SIZE': 5,
    
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

from datetime import timedelta
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
    'BLACKLIST_AFTER_ROTATION': True,
    'ROTATE_REFRESH_TOKENS': True,
    # 'ROTATE_REFRESH_TOKENS': False,
    
    'ACCESS_TOKEN_LIFETIME': timedelta(days=60),
    # 'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=60),
    
    "UPDATE_LAST_LOGIN": True,
}

CORS_ORIGIN_ALLOW_ALL = True

# ==================== Rest Frame Work Configurations End====================
# ================================================================================




MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware'
]

ROOT_URLCONF = 'buyolex_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'buyolex_config.wsgi.application'


# Database======================================================================================
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "0").strip().lower() in ("url","1")
if DATABASE_TYPE:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    ENGINE_MAP = {
        "sqlite": "django.db.backends.sqlite3",
        "postgres": "django.db.backends.postgresql",
        "mysql": "django.db.backends.mysql",
    }
    DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
    DB_NAME = BASE_DIR / os.getenv("DATABASE_NAME", "db.sqlite3") if DB_ENGINE == "sqlite" else os.getenv("DATABASE_NAME")
    DATABASES = {
        "default": {
            "ENGINE": ENGINE_MAP.get(DB_ENGINE, "django.db.backends.sqlite3"),
            "NAME": DB_NAME,
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", ""),
            "PORT": os.getenv("DB_PORT", ""),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = 'media/'
MEDIA_ROOT = os.getenv('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))




# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.CustomUser'

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home_page'
LOGIN_URL = 'login'

# default is ~2.5 MB; bump to e.g. 20 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587  # SMTP server port (587 for TLS, 465 for SSL)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_password'
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'your_email@example.com'
