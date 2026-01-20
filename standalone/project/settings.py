# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o6hk&s9ffvgn5g3k$))i=@7k16g#ai@oom4m#d)bw(oumpp022'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('ENV', 'prd') != 'prd'

# Allow all hosts by default, but can be overridden via environment variable
if os.environ.get('ALLOWED_HOSTS'):
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')
else:
    ALLOWED_HOSTS = ['*']

# CSRF settings for production
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8008',
    'http://127.0.0.1:8008',
]

# Allow additional trusted origins from environment variable
if os.environ.get('CSRF_TRUSTED_ORIGINS'):
    CSRF_TRUSTED_ORIGINS.extend(os.environ.get('CSRF_TRUSTED_ORIGINS').split(','))


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dynamicdns',
    'project',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'project.urls'

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

if os.environ.get('POSTGRES_HOST'):
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'HOST':     os.environ.get('POSTGRES_HOST', '127.0.0.1'),
            'NAME':     os.environ.get('POSTGRES_DATABASE', 'dynamicdns'),
            'USER':     os.environ.get('POSTGRES_USER', 'root'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'password'),
            'OPTIONS': {
                'options': '-c timezone=utc'
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.sqlite3',
            'NAME':     os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


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


DYNAMICDNS_PROVIDERS = {
    'dummy': {
        'plugin': 'dynamicdns.plugins.Dummy',
    },
    # 'rackspace': {
    #     'plugin': 'dynamicdns.plugins.Rackspace',
    #     'username': 'YOUR_USERNAME',
    #     'api_key': 'YOUR_API_KEY',
    # },
    # 'digitalocean': {
    #     'plugin': 'dynamicdns.plugins.DigitalOcean',
    #     'client_id': 'YOUR_CLIENT_ID',
    #     'api_key': 'YOUR_API_KEY',
    # },
    # 'aws': {
    #     'plugin': 'dynamicdns.plugins.AWS',
    #     'aws_access_key_id': 'YOUR_AWS_ACCESS_KEY_ID',
    #     'aws_secret_access_key': 'YOUR_AWS_SECRET_ACCESS_KEY',
    #     'aws_region': 'us-east-1',
    #     'hosted_zone_id': 'YOUR_HOSTED_ZONE_ID',
    # },
}

# DNS provider plugins can be configured via environment variables (useful with Docker)
if 'RACKSPACE_USERNAME' in os.environ:
    DYNAMICDNS_PROVIDERS['rackspace'] = {
        'plugin': 'dynamicdns.plugins.Rackspace',
        'username': os.environ.get('RACKSPACE_USERNAME'),
        'api_key': os.environ.get('RACKSPACE_API_KEY'),
    }
if 'DIGITALOCEAN_CLIENT_ID' in os.environ:
    DYNAMICDNS_PROVIDERS['digitalocean'] = {
        'plugin': 'dynamicdns.plugins.DigitalOcean',
        'client_id': os.environ.get('DIGITALOCEAN_CLIENT_ID'),
        'api_key': os.environ.get('DIGITALOCEAN_API_KEY'),
    }
if 'AWS_ACCESS_KEY_ID' in os.environ:
    DYNAMICDNS_PROVIDERS['aws'] = {
        'plugin': 'dynamicdns.plugins.AWS',
        'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'aws_region': os.environ.get('AWS_REGION', 'us-east-1'),
        'hosted_zone_id': os.environ.get('AWS_HOSTED_ZONE_ID'),
    }
if 'HETZNER_API_TOKEN' in os.environ:
    DYNAMICDNS_PROVIDERS['hetzner'] = {
        'plugin': 'dynamicdns.plugins.Hetzner',
        'api_token': os.environ.get('HETZNER_API_TOKEN'),
        'zone_id': os.environ.get('HETZNER_ZONE_ID'),
    }

# Default primary key field type for Django 4.2+
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
