
import sys
import concurrent.futures
from django.core.management.base import BaseCommand

from rawdat.models import Venue, Race
from miner.utilities.urls import build_race_results_url
from miner.utilities.scrape import (
    get_node_elements,
    get_rows_of_length,
    save_single_bets,
    get_single_bets
)
from pww.models import Metric


class Command(BaseCommand):


    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)

    def get_venue_results(self, venue):
        year = sys.argv[3]
        self.stdout.write("Processing {} {}".format(venue, year))
        for race in Race.objects.filter(
            chart__program__venue=venue,
            chart__program__date__year=year):
            chart = race.chart
            date = chart.program.date
            results_url = build_race_results_url(
                venue.code,
                date.year,
                date.month,
                date.day,
                chart.time,
                race.number)
            print(results_url)
            page_rows = get_node_elements(results_url, '//tr')
            bet_rows = get_rows_of_length(page_rows, 5)
            # print(bet_rows)
            # print(len(bet_rows))
            single_bets = None
            if len(bet_rows) > 1:
                # print(">1")
                single_bets = get_single_bets(bet_rows)
                print(single_bets)
                save_single_bets(race, single_bets)



    def handle(self, *args, **options):

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(
                self.get_venue_results,
                Venue.objects.filter(is_active=True))
