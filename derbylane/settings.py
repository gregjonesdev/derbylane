ROOT_URLCONF = "derbylane.urls"
#
from settings.base import *

DEBUG = False
# set_urlconf("derbylane.urls")
# print(settings)
#
# ALLOWED_HOSTS = [
#     'www.cashdog.life',
#     'cashdog.life',
#     '144.126.219.69',
#     'localhost',
#     '127.0.0.1']


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
