import sys
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from concurrent.futures import ThreadPoolExecutor

from miner.utilities.urls import build_race_results_url
from miner.utilities.common import get_node_elements
from miner.utilities.constants import chart_times
from miner.utilities.comments import no_elements, success
from miner.utilities.models import get_program, get_chart, get_race
from miner.utilities.scrape_results import process_url, has_results

from rawdat.models import ScannedUrl, Venue

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)
        parser.add_argument('--month', type=int)

    def get_scan(self, url):
        try:
            scan = ScannedUrl.objects.get(address=url)
        except ObjectDoesNotExist:
            new_scan = ScannedUrl(address=url)
            new_scan.set_fields_to_base()
            new_scan.save()
            scan = new_scan
        return scan

    def update_scan(self, scan, comment):
        scan.comment = comment
        if comment in [no_elements, success]:
            scan.completed = True
        scan.save()

    def scan_day(self, venue_code, month, year, day):
        venue = Venue.objects.get(code=venue_code)
        program = get_program(
            venue,
            "{}-{}-{}".format(
                year,
                str(month).zfill(2),
                str(day).zfill(2)
            )
        )
        print("Scanning: {} {}/{}/{}".format(venue_code, month, day, year))
        for time in chart_times:
            chart = get_chart(program, time)
            number = 1
            while number <= 30:
                comment = None
                url = build_race_results_url(
                    venue_code,
                    year,
                    str(month).zfill(2),
                    str(day).zfill(2),
                    time,
                    str(number).zfill(2))
                scan = self.get_scan(url)
                if not scan.completed:
                    if has_results(url):
                        race = get_race(chart, number)
                        try:
                            comment = process_url(url, race)
                        except:
                            comment = "Errored:"
                            print(url)
                    else:
                        comment = no_elements
                    self.update_scan(scan, comment)
                number += 1

    def is_valid_past_date(self, month, year, day):
        try:
            date = datetime.datetime(year, month, day)
            if date < datetime.datetime.now():
                return True
        except ValueError:
            pass

    def scan_month(self, venue_code, month, year):
        day = 28
        while day <= 31:
            if self.is_valid_past_date(month, year, day):
                self.scan_day(venue_code, month, year, day)
            day += 1

    def get_venue_results(self, venue_code):
        year = int(sys.argv[3])
        month = int(sys.argv[5])
        while month <= 12:
            self.scan_month(venue_code, month, year)
            month += 1


    def handle(self, *args, **options):
        # venue_codes = ['TS', 'WD', 'SL']
        # with ThreadPoolExecutor() as executor:
        #     executor.map(self.get_venue_results, venue_codes)

        self.get_venue_results('WD')
