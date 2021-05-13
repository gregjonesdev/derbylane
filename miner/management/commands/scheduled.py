import datetime

from django.core.management.base import BaseCommand

from miner.utilities.scrape import scan_scheduled_charts
from rawdat.models import Program, Venue


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Scheduled script..")
        dates = self.get_dates()
        for venue in Venue.objects.filter(is_active=True):
            print("Processing {}".format(venue.name))
            for date in dates:
                print("Scanning {}/{} Charts".format(date.month, date.day))
                scan_scheduled_charts(venue, date.year, date.month, date.day)

    def get_dates(self):
        dates = []
        i = -3
        while i < 3:
            offset = datetime.timedelta(days=i)
            dates.append(datetime.datetime.now() + offset)
            i += 1
        return dates
