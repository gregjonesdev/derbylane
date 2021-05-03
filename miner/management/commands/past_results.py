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

    def process_venue(self, venue):
        self.stdout.write("Processing")
        # year = sys.argv[3]
        # self.stdout.write("Processing {} {}".format(venue, year))

    def handle(self, *args, **options):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(
                self.process_venue,
                Venue.objects.filter(is_active=True))
