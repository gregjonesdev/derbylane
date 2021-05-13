from datetime import datetime
from django.core.management.base import BaseCommand

from rawdat.models import Race

from miner.utilities.urls import (
    build_almanac_url,
    build_forecast_url,
    build_race_results_url,
    build_entries_url)

class Command(BaseCommand):

    def handle(self, *args, **options):
        now = datetime.now().date()
        for race in Race.objects.all():
            chart = race.chart
            program = chart.program

            print("{} {} {} Race {}".format(
                program.venue.code,
                program.date,
                chart.time,
                race.number
            ))
            print("Grade: {}\tDistance: {} yds".format(race.grade.name, race.distance))
            print("-------------------------------------------")
            for p in race.participant_set.all():
                print("{}\t{}\t{}\t{}".format(
                    p.post,
                    p.dog.name,
                    p.post_weight,
                    p.final,
                ))
            weather = program.weather
            print("Weather:")
            print("{}\t{}/{}\t{}\t{} mph\n".format(
                program.date,
                weather.max_temp,
                weather.min_temp,
                weather.percipitation,
                weather.wind))
            if program.date < now:
                print(build_race_results_url(
                    program.venue.code,
                    program.date.year,
                    program.date.month,
                    program.date.day,
                    chart.time,
                    race.number
                    ))
                print("\n")
                try:
                    print(build_almanac_url(program))
                except AttributeError:
                    pass
            else:
                print(build_entries_url(
                    program.venue.code,
                    program.date.year,
                    program.date.month,
                    program.date.day,
                    chart.time,
                    race.number
                    ))
                print("\n")
                try:
                    print(build_forecast_url(program))
                except AttributeError:
                    pass

            print("-------------------------------------------\n\n")
