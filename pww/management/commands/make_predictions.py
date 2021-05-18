import datetime

from django.core.management.base import BaseCommand
from rawdat.models import Race
from pww.models import Prediction, Metric

from pww.utilities.metrics import build_race_metrics


class Command(BaseCommand):


    def handle(self, *args, **options):
        # races = Race.objects.filter(chart__program__date="2021-04-17", chart__program__venue__code="WD")[:1]
        # build_race_metrics(races[0])
        # Get today's races
        # for each race, filter metrics
        # create 1 or 2 csv

        for race in Race.objects.filter(
            chart__program__date=datetime.date.today()):
            print(race.chart.program.venue.name)
            print(race.chart.time)
            print(race.number)
            print(race.grade)
            print(race.distance)
            for participant in race.participant_set.all():
                print("{} | {}".format(participant.post, participant.dog.name))
