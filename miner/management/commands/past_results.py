import sys
import concurrent.futures
import requests

from django.core.management.base import BaseCommand

from rawdat.models import (
    Venue,
    VenueScan
    )

from rawdat.utilities.constants import (
    chart_times,
)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)
        parser.add_argument('--venue', type=str)

    def scan_month(self, venue, month, year):
        day = 1
        while day < 32:
            for time in chart_times:

        # create history scan

    def process_venue(self, venue):
        year = sys.argv[3]
        self.stdout.write("Processing {} {}".format(venue, year))
        month = 1
        while month <= 12:
            if not self.scan_complete(venue, month, year):
                self.scan_month(venue, month, year)


    def scan_complete(self, venue, month, year):
        try:
            VenueScan.objects.get(
                venue=venue,
                month=month,
                year=year
            )
            return True
        except ObjectDoesNotExist:
            return False


    def process_active_venues(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(
                self.process_venue,
                Venue.objects.filter(is_active=True))

    def handle(self, *args, **options):
        year = sys.argv[3]
        try:
            self.process_venue(
                Venue.objects.get(code=sys.argv[5]),
                year)
        except IndexError:
            self.process_active_venues()
