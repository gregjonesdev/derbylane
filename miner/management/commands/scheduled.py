import datetime

from django.core.management.base import BaseCommand

from rawdat.models import (
    Program,
    Venue,
    )

from miner.utilities.scrape import scan_chart_times

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Scheduled script..")
        dates = self.get_dates()
        for venue in Venue.objects.filter(is_active=True):
            for date in dates:
                scan_chart_times(venue, date.year, date.month, date.day)

    def get_dates(self):
        dates = []
        i = 0
        while i < 3:
            offset = datetime.timedelta(days=i)
            dates.append(datetime.datetime.now() + offset)
            i += 1
        return dates
