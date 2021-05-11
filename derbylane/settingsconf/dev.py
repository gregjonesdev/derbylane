from .base import *

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'Topsecretkey'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'derbylane',
        'USER': 'greg',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
