from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    'www.cashdog.life',
    'cashdog.life',
    '144.126.219.69',
    'localhost',
    '127.0.0.1']


from django.conf import settings
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'derbylane',
        'USER': 'derbylaneuser',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    }
}
