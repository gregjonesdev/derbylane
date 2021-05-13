import sys
import concurrent.futures

from django.core.management.base import BaseCommand

from rawdat.models import (
    Venue,
    VenueScan,
    )

from miner.utilities.scrape import scan_history_charts

from miner.utilities.weather import build_weather_from_almanac

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)
        parser.add_argument('--venue', type=str)

    def scan_month(self, venue, month, year):
        day = 1
        while day <= 31:
            scan_history_charts(venue, year, month, day)
            day += 1
        # self.create_venue_scan(venue, year, month)

    def create_venue_scan(self, venue, year, month):
        try:
            venue_scan = VenueScan.objects.get(
                venue=venue,
                year=year,
                month=month
            )
        except ObjectDoesNotExist:
            new_scan = VenueScan.objects.get(
                venue=venue,
                year=year,
                month=month
            )
            new_scan.set_fields_to_base()
            new_scan.save()

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
