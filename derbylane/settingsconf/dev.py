from .base import *

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q^w%k)r#m4mz0n5m55w-9e)q#gs50(v^0f=)_e!#=qok$yg^6p'

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
print(os.path.dirname(BASE_DIR))
CRONJOBS = [
    ('* * * * * cd {}'.format(os.path.dirname(BASE_DIR)), 'miner.cron.jobs.test',  '>> ~/cron_job.log')
]
