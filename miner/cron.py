from django.core import management

from rawdat.models import CronJob

def my_cron_job():
    management.call_command('crontest')
