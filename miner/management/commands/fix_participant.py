import datetime
import random
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from rawdat.models import Race, Condition
from pww.models import Participant_Prediction, WekaModel
from pww.utilities.metrics import build_race_metrics
from miner.utilities.urls import build_race_results_url
from miner.utilities.scrape_results import update_race_condition

bets = ["W", "P", "S", "WP", "PS", "WPS"]

class Command(BaseCommand):

    def handle(self, *args, **options):

        for race in Race.objects.filter(
            condition__name__isnull=True
        ):
            url = build_race_results_url(
                    race.chart.program.venue.code,
                    race.chart.program.date.year,
                    race.chart.program.date.month,
                    race.chart.program.date.day,
                    race.chart.time,
                    race.number)
            print(url)
            # update_race_condition(race, url)
