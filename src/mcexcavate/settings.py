import os

from django.core.exceptions import ImproperlyConfigured


def _load_env_file(env_path):
    if not os.path.exists(env_path):
        return

    with open(env_path, encoding='utf-8') as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            if value and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]

            os.environ.setdefault(key, value)


def _get_env(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and (value is None or value == ''):
        raise ImproperlyConfigured(f"Set the {name} environment variable.")
    return value


def _get_bool_env(name, default=False):
    value = _get_env(name, default=str(default))
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
_load_env_file(os.path.join(PROJECT_ROOT, '.env'))


SECRET_KEY = _get_env('DJANGO_SECRET_KEY', required=True)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _get_bool_env('DJANGO_DEBUG', default=False)


# Email settings
EMAIL_BACKEND = 'mcexcavate.email_backend.IPv4EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = _get_env('DJANGO_EMAIL_HOST_USER', required=True)
EMAIL_HOST_PASSWORD = _get_env('DJANGO_EMAIL_HOST_PASSWORD', required=True)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_TIMEOUT = 30


# Threshold for spooling uploads to disk; this is not an upload size limit.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB


ALLOWED_HOSTS = ['172.105.25.80', '127.0.0.1', 'mcexcavate.com', 'www.mcexcavate.com']


# PhoneNumberField Settings
PHONENUMBER_DEFAULT_REGION = "CA"


RECAPTCHA_PUBLIC_KEY = _get_env('DJANGO_RECAPTCHA_PUBLIC_KEY', required=True)
RECAPTCHA_PRIVATE_KEY = _get_env('DJANGO_RECAPTCHA_PRIVATE_KEY', required=True)
RECAPTCHA_REQUIRED_SCORE = 0.5

try:
    import django_recaptcha  # noqa: F401
except ModuleNotFoundError:
    RECAPTCHA_APP = 'captcha'
else:
    RECAPTCHA_APP = 'django_recaptcha'


# Application definition
INSTALLED_APPS = [
    RECAPTCHA_APP,
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'phonenumber_field',
    'ckeditor',
    'ckeditor_uploader',
    'gallery',
    'project',
    'blog',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mcexcavate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'mcexcavate.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


CKEDITOR_UPLOAD_PATH = "blog-uploads/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')
MEDIA_URL = '/media/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
