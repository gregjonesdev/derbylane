from .base import *

DEBUG = True

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
