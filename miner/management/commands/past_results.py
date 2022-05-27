import sys
from concurrent.futures import ThreadPoolExecutor
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.core.management.base import BaseCommand

from rawdat.models import Venue

from miner.utilities.scrape import scan_history_charts, single_url_test

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)

    def scan_month(self, venue, month, year):
        self.stdout.write("Processing {} {}/{}".format(venue, month, year))
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


    def get_venue_results(self, venue_code):
        venue = Venue.objects.get(code=venue_code)
        year = sys.argv[3]
        month = 1
        while month <= 12:
            self.scan_month(venue, month, year)
            month += 1


    def handle(self, *args, **options):

        venue_codes = ['TS', 'WD', 'SL']

        self.get_venue_results('TS')

        # with ThreadPoolExecutor() as executor:
        #     executor.map(self.get_venue_results, venue_codes)





def download_images(url):
    img_name = img_url.split('/')[3]
    img_bytes = requests.get(img_url).content
    with open(img_name, 'wb') as img_file:
         img_file.write(img_bytes)
         print(f"{img_name} was downloaded")


 #this is Similar to map(func, *iterables)
