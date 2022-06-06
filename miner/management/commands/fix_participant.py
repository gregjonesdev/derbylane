import datetime
import random
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from rawdat.models import Race, Condition
from pww.models import Participant_Prediction, WekaModel
from pww.utilities.metrics import get_raw_race_metrics
from miner.utilities.urls import get_results_url_for_race
from miner.utilities.scrape_results import update_race_condition, save_race_settings, get_parsed_results_race_setting

bets = ["W", "P", "S", "WP", "PS", "WPS"]

class Command(BaseCommand):

    def handle(self, *args, **options):
        race = Race.objects.get(
            chart__program__venue__code="TS",
            chart__program__date="2022-05-30",
            number=3
        )
        metrics = get_raw_race_metrics(race)
        for metric in metrics:
            print(metric)
