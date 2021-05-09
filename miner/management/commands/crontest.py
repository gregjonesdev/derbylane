from django.core.management.base import BaseCommand

from rawdat.models import CronJob

class Command(BaseCommand):

    def handle(self, *args, **options):
        new_job = CronJob(
            type="Success"
        )
        new_job.set_fields_to_base()
        new_job.save()
