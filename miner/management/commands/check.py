from django.core.management.base import BaseCommand

from rawdat.models import Race

from miner.utilities.urls import (
    build_almanac_url,
    build_race_results_url)

class Command(BaseCommand):

    def handle(self, *args, **options):
        for race in Race.objects.all():
            chart = race.chart
            program = chart.program
            print("{} {} {} Race {}".format(
                program.venue.code,
                program.date,
                chart.time,
                race.number
            ))
            print("--------------------------------------")
            print(build_race_results_url(
                program.venue.code,
                program.date.year,
                program.date.month,
                program.date.day,
                chart.time,
                race.number
                ))
            print("\n")
            for p in race.participant_set.all():
                print("{}\t{}\t{}".format(
                    p.post,
                    p.dog.name,
                    p.post_weight,

                ))
            try:
                print(program.weather)
                print(build_almanac_url(program))
            except AttributeError:
                pass
