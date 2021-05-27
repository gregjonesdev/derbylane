from django.core.management.base import BaseCommand

from pww.models import Prediction
from rawdat.models import Race

bet_cost = 2

class Command(BaseCommand):

    def handle(self, *args, **options):
        pass
        # grade =
        # distance =
        # venue =

        # get all races (2019)
        races = Race.objects.filter(
            chart__program__date__year=2019,
            distance=distance,
            venue=venue
        )
        # for each participant,save prediction with each classifier.
        # get final


        # classifier =
