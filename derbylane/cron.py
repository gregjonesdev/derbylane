from django.core import management

def my_cron_job():
    management.call_command('crontest')
