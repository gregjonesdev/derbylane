import sys
import concurrent.futures
import requests

from django.core.management.base import BaseCommand

from rawdat.models import (
    Venue,
    VenueScan,
    )

from miner.utilities.scrape import build_daily_charts



class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)
        parser.add_argument('--venue', type=str)

    def scan_month(self, venue, month, year):
        day = 1
        while day <= 31:
            build_daily_charts(venue, month, year, day)
            day += 1
        # create history scan

    def get_venue_results(self, venue):
        year = sys.argv[3]
        self.stdout.write("Processing {} {}".format(venue, year))
        month = 1
        while month <= 12:
            if not self.scan_complete(venue, month, year):
                self.scan_month(venue, month, year)
            month += 1


    def scan_complete(self, venue, month, year):
        return VenueScan.objects.filter(
                venue=venue,
                month=month,
                year=year).exists()


    def process_active_venues(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(
                self.get_venue_results,
                Venue.objects.filter(is_active=True))

    def handle(self, *args, **options):
        year = sys.argv[3]
        try:
            self.get_venue_results(
                Venue.objects.get(code=sys.argv[5]))
        except IndexError:
            self.process_active_venues()
