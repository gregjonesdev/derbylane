from django.core import management
from rawdat.models import CronJob

def test():
    new_job = CronJob(
        type="Raw"
    )
    new_job.set_fields_to_base()
    new_job.save()
