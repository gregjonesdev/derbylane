#!/bin/bash
DJANGO_SETTINGS_MODULE=derbylane.settings
DJANGO_SECRET_KEY= os.environ.get('SECRET_KEY')

/home/greg/derbylane/dl_env/bin/python /home/greg/derbylane/dl_env/derbylane/manage.py crontest
