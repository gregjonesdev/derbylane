import sys
import concurrent.futures
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.core.management.base import BaseCommand

from rawdat.models import Venue

from miner.utilities.scrape import scan_history_charts, single_url_test

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)

    def scan_month(self, venue, month, year):
        day = 1
        while day <= 31:
            try:
                datetime.datetime(
                    int(year),
                    int(month),
                    int(day))
                scan_history_charts(venue, year, month, day)
            except:
                pass
            day += 1


    def get_venue_results(self, year, venue):
        self.stdout.write("Processing {} {}".format(venue, year))
        month = 1
        while month <= 12:
            self.scan_month(venue, month, year)
            month += 1


    def handle(self, *args, **options):
        year = sys.argv[3]
        venue_codes = ['TS', 'WD']
        for venue_code in venue_codes:
            self.get_venue_results(
                year,
                Venue.objects.get(code=venue_code)
            )
