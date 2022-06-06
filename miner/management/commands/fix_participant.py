import datetime
import random
import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand

from rawdat.models import Race, Participant
from pww.models import Participant_Prediction, WekaModel
from pww.utilities.metrics import get_raw_race_metrics
from miner.utilities.urls import get_results_url_for_race
from miner.utilities.scrape_results import update_race_condition, save_race_settings, get_parsed_results_race_setting

bets = ["W", "P", "S", "WP", "PS", "WPS"]

class Command(BaseCommand):

    def handle(self, *args, **options):
        for race in Race.objects.all():
            i = 1
            while i < 9:
                try:
                    Participant.objects.get(
                        race=race,
                        post=int(i)
                    )
                except MultipleObjectsReturned:
                    print(race.uuid)
                i += 1
