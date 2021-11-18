
from django.core.management.base import BaseCommand
import datetime
from rawdat.models import Race
from miner.utilities.urls import build_race_results_url
from miner.utilities.scrape import (
    get_node_elements,
    get_rows_of_length,
    save_single_bets,
    get_single_bets
)
from pww.models import Metric


class Command(BaseCommand):

    def handle(self, *args, **options):

        today = datetime.date.today()
        print(today)
        for race in Race.objects.filter(
            chart__program__date="2021-06-23"):
            chart = race.chart
            program = chart.program
            date = program.date
            results_url = build_race_results_url(
                program.venue.code,
                date.year,
                date.month,
                date.day,
                chart.time,
                race.number)
            print(results_url)

            for participant in race.participant_set.all():
                try:
                    win = participant.straight_wager.win
                except:
                    win = ""
                print("{}\t{}\t{}".format(
                    participant.post,
                    participant.dog.name[:8],
                    participant.final,
                    win))
