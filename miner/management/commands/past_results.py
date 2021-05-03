import sys
import concurrent.futures
import requests

from django.core.management.base import BaseCommand

from rawdat.models import (
    Venue,
    )

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)
        parser.add_argument('--venue', type=str)

    def process_venue(self, venue):
        year = sys.argv[3]
        self.stdout.write("Processing {} {}".format(venue, year))

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
