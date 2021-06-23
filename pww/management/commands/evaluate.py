from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from pww.models import Prediction


class Command(BaseCommand):

    def get_bet_size(self, value):
        if value < 1:
            return 10.00
        elif value <2:
            return 5.00
        elif value <3:
            return 2.00
        else:
            return None


    def handle(self, *args, **options):
        print("Starting")

        bets = {}

        for prediction in Prediction.objects.filter(
            smo__isnull=False,
            participant__final__isnull=False):
            # print(self.get_bet_size(prediction.smo))
            race = prediction.participant.race
            grade_name = race.grade.name
            distance = race.distance
            venue_code = race.chart.program.venue.code

            if not venue_code in bets.keys():
                bets[venue_code] = {}
            if not grade_name in bets[venue_code].keys():
                bets[venue_code][grade_name] = {}
            if not str(distance) in bets[venue_code][grade_name].keys():
                bets[venue_code][grade_name][str(distance)] = {
                    "bet_count": 0
                }
            bets[venue_code][grade_name][str(distance)]["bet_count"] += 1


        print(bets)

            # venue_grade_distance = bets['venue_code']['grade_name']['distance']
            # if not venue_grade_distance['bet_count']:
            #      venue_grade_distance['bet_count'] = 1
            # else:
            #     venue_grade_distance['bet_count'] += 1
