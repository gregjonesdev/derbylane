import datetime
import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from rawdat.models import Participant
from pww.models import Participant_Prediction

from pww.utilities.metrics import build_race_metrics


bets = ["W", "P", "S", "WP", "PS", "WPS"]

class Command(BaseCommand):

    def handle(self, *args, **options):

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        for participant in Participant.objects.filter(race__chart__program__date__gte=today):

            random_int = random.randint(3500, 5500)
            try:
                pred = Participant_Prediction.objects.get(participant=participant)
            except ObjectDoesNotExist:
                new_pred = Participant_Prediction(
                    participant = participant
                )
                new_pred.set_fields_to_base()
                pred = new_pred
            pred.smoreg = random_int/1000
            pred.save()
