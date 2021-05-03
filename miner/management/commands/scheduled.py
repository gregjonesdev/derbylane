import datetime

from django.core.management.base import BaseCommand

from rawdat.models import (
    Program,
    )

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Scheduled script..")
        active_venues = Venue.objects.filter(is_active=True)
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        all_scaled_metrics = {}
        for program in Program.objects.filter(
            date__range=(yesterday, today)):
            if program.venue in active_venues:
                pass
                # weather
                # race data
