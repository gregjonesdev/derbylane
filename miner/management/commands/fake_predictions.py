import datetime
import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from rawdat.models import Participant
from pww.models import Participant_Prediction, WekaModel
from pww.utilities.metrics import build_race_metrics


bets = ["W", "P", "S", "WP", "PS", "WPS"]

class Command(BaseCommand):

    def handle(self, *args, **options):

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        for participant in Participant.objects.filter(race__chart__program__date__gte=today):
            # bet_recommendation = Bet_Recommendation.objects.filter(
            #     model = WekaModel.objects.first()
            # )[0]
            models = WekaModel.objects.filter(
                venue=participant.race.chart.program.venue,
                grade=participant.race.grade
            )
            random_int = random.randint(4700, 5000)
            for model in models:
                prediction = Participant_Prediction(
                    participant = participant,
                    smoreg = random_int/1000,
                    model = model
                )
                prediction.set_fields_to_base()
                prediction.save()
