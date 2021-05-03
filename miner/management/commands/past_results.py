import sys
import concurrent.futures
import requests

from django.core.management.base import BaseCommand

from rawdat.models import (
    Venue,
    VenueScan,
    )

from rawdat.utilities.constants import (
    chart_times,
)

from rawdat.utilities.methods import (
    get_program,
    get_chart,
    get_race
)

from miner.utilities.scrape import (
    build_results_url,
    has_race_data,
    save_race_data,
)


allowed_attempts = 3
max_races_per_chart = 30

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)
        parser.add_argument('--venue', type=str)

    def scan_chart(self, venue, month, year, day, time):
        number = 1
        failed_attempts = 0
        while failed_attempts <= allowed_attempts and number <= 30:
            target_url = build_results_url(
                venue.code,
                year,
                month,
                day,
                time,
                number)
            if has_race_data(target_url):
                program = get_program(
                    venue,
                    year,
                    month,
                    day)
                chart = get_chart(program, time)
                race = get_race(
                    chart,
                    number)
                save_race_data(target_url)
            else:
                failed_attempts += 1
            number += 1


    def scan_month(self, venue, month, year):
        day = 1
        while day <= 31:
            for time in chart_times:
                self.scan_chart(venue, month, year, day, time)
            day += 1
        # create history scan

    def process_venue(self, venue):
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
                self.process_venue,
                Venue.objects.filter(is_active=True))

    def handle(self, *args, **options):
        year = sys.argv[3]
        try:
            self.process_venue(
                Venue.objects.get(code=sys.argv[5]))
        except IndexError:
            self.process_active_venues()
