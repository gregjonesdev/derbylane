import datetime
import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from miner.utilities.common import get_node_elements
from miner.utilities.scrape import single_url_test
from miner.utilities.urls import build_race_results_url
from rawdat.models import Participant
from pww.models import Prediction

from pww.utilities.metrics import build_race_metrics


bets = ["W", "P", "S", "WP", "PS", "WPS"]

class Command(BaseCommand):

    def handle(self, *args, **options):

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        for participant in Participant.objects.filter(race__chart__program__date__gte=today):
            try:
                pred = Prediction.objects.get(participant=participant)
            except ObjectDoesNotExist:
                new_pred = Prediction(
                    participant = participant
                )
                new_pred.set_fields_to_base()
                pred = new_pred
            pred.bet = bets[random.randint(0, 5)]
            pred.save()
