import datetime
import random
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from rawdat.models import Race
from pww.models import Participant_Prediction, WekaModel
from pww.utilities.metrics import build_race_metrics


bets = ["W", "P", "S", "WP", "PS", "WPS"]

class Command(BaseCommand):

    def handle(self, *args, **options):

        i = 0
        for race in Race.objects.filter(chart__program__date__gte="2022-01-01"):
            participants = race.participant_set.all()
            if len(participants) > 8:
                i += 1
                print("\n\n")
                for participant in participants:
                    print("{}\t{}\t{}\t{}\t{}\t{}".format(
                        participant.dog.name,
                        participant.post,
                        participant.off,
                        participant.eighth,
                        participant.straight,
                        participant.created_at
                    ))
                    if datetime.date(2022, 5, 28) <= participant.created_at <= datetime.date(2022, 5, 30):
                        participant.delete()

        print("{} Races affected".format(i))
