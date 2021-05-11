import os

from .settingsconf.base import *

LOGIN_URL = 'two_factor:login'

# this one is optional
LOGIN_REDIRECT_URL = 'frontpage'
LOGOUT_REDIRECT_URL = "/"


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
