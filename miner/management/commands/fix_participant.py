import datetime
import random
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from rawdat.models import Race, Condition
from pww.models import Participant_Prediction, WekaModel
from pww.utilities.metrics import build_race_metrics
from miner.utilities.urls import get_results_url_for_race
from miner.utilities.scrape_results import update_race_condition, save_race_settings, get_parsed_results_race_setting

bets = ["W", "P", "S", "WP", "PS", "WPS"]

class Command(BaseCommand):

    def handle(self, *args, **options):

        for race in Race.objects.filter(
            chart__program__date__gte="2022-01-01"):    
            for participant in race.participant_set.all():
                print(participant.actual_running_time)
            build_race_metrics(race)
