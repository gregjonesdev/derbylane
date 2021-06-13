from django.core.management.base import BaseCommand

from rawdat.models import Participant, Dog
from miner.utilities.urls import build_race_results_url


class Command(BaseCommand):

    def handle(self, *args, **options):
        dog = Dog.objects.get(name="CET EASI ELI")
        for part in dog.participant_set.all():
            race = part.race
            chart = race.chart
            program = chart.program
            venue = program.venue
            print(build_race_results_url(
                venue.code,
                program.date.year,
                program.date.month,
                program.date.day,
                chart.time,
                race.number))
