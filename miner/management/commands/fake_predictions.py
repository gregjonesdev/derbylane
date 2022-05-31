import datetime
import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from rawdat.models import Participant
from pww.models import Participant_Prediction, WekaModel, Bet_Recommendation

from pww.utilities.metrics import build_race_metrics


bets = ["W", "P", "S", "WP", "PS", "WPS"]

class Command(BaseCommand):

    def handle(self, *args, **options):

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        for participant in Participant.objects.filter(race__chart__program__date__gte=today):
            bet_recommendation = Bet_Recommendation.objects.filter(
                model = WekaModel.objects.first()
            )[0]
            random_int = random.randint(3900, 4080)
            prediction = Participant_Prediction(
                participant = participant,
                smoreg = random_int/1000,
                recommendation = bet_recommendation
            )
            prediction.set_fields_to_base()
            prediction.save()
