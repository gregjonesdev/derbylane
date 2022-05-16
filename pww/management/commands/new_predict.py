import datetime

from django.core.management.base import BaseCommand

from pww.utilities.classifiers import recommendations
from rawdat.models import Race


betting_venues = ["WD", "TS", "SL"]

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str)

    def handle(self, *args, **options):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        for race in Race.objects.filter(chart__program__date__gte=today):
            print("{} {} Race {} Grade {}".format(
                race.chart.program.venue.name,
                race.chart.time,
                race.number,
                race.grade.name
            ))
            new_key = "{}_{}".format(
                race.chart.program.venue.code,
                race.grade.name)
            for race_type in recommendations:
                if new_key in race_type:
                    print(race_type)
            print("/n")        
