import os
import json

# with open('/etc/config.json') as config_file:
#     config = json.load(config_file)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#SECRET_KEY = config["SECRET_KEY"]
SECRET_KEY = 'dc578pv-t)gq+k)yw+rd^2(pd)pji*x5til*kzdjb1@byr3+)h'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

#EMAIL_HOST = 'mail.privateemail.com'
EMAIL_HOST = 'smtp.gmail.com'

#EMAIL_HOST_USER = 'info@mcexcavate.com'
#EMAIL_HOST_PASSWORD = 'Duke3818#'

EMAIL_HOST_USER = 'mcexcavate.ottawa@gmail.com'
EMAIL_HOST_PASSWORD = 'vfmr olja dsgd dbca'

EMAIL_USE_TLS = True
EMAIL_PORT = 587 
#EMAIL_HOST_USER = config["EMAIL_HOST_USER"]
#EMAIL_HOST_PASSWORD = config["EMAIL_HOST_PASSWORD"]

# Max uploaded file size
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB

ALLOWED_HOSTS = ['172.105.25.80', '127.0.0.1', 'mcexcavate.com', 'www.mcexcavate.com']

# PhoneNumberField Settings
#PHONENUMBER_DB_FORMAT = 
PHONENUMBER_DEFAULT_REGION = "CA"
#PHONENUMBER_DEFAULT_FORMAT = 

# Captcha Keys
RECAPTCHA_PUBLIC_KEY = '6LfG1aIqAAAAAPMeB-NJ3d3Rvr0ehi9mmb1GaO4m'
RECAPTCHA_PRIVATE_KEY = '6LfG1aIqAAAAAHcIJyPfaZ4_9L92OuoMEl0G1rEO'

# Application definition
INSTALLED_APPS = [
    'django_recaptcha',
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

    # my app
    'gallery',
    'project',
    'blog'
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


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

CKEDITOR_UPLOAD_PATH = "blog-uploads/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    ]

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')
MEDIA_URL = '/media/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'