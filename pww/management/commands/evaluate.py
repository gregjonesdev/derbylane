from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from pww.models import Prediction


class Command(BaseCommand):

    def print_report(self, bets):
        print("{}\t{}\t{}\t{}\t{}\t\t{}\t\t{}".format(
            "Venue",
            "Grade",
            "Distance",
            "Bets Made",
            "Spent",
            "Earned",
            "Profit Per Bet"
        ))
        for venue_code in bets.keys():
            for grade_name in bets[venue_code].keys():
                for distance in bets[venue_code][grade_name].keys():
                    venue_grade_distance = bets[venue_code][grade_name][distance]
                    ret = venue_grade_distance["return"]
                    bet = venue_grade_distance["bet_count"]
                    spent = venue_grade_distance["spent"]
                    try:
                        ppb = (float(ret)-float(spent))/bet
                    except:
                        ppb = "N/A"
                    print("{}\t{}\t{}\t\t{}\t\t{}\t\t{}\t\t{}".format(
                        venue_code,
                        grade_name,
                        distance,
                        bet,
                        spent,
                        ret,
                        ppb
                    ))

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
            participant = prediction.participant
            race = participant.race
            grade_name = race.grade.name
            distance = race.distance
            venue_code = race.chart.program.venue.code

            if not venue_code in bets.keys():
                bets[venue_code] = {}
            if not grade_name in bets[venue_code].keys():
                bets[venue_code][grade_name] = {}
            str_dist = str(distance)
            if not str_dist in bets[venue_code][grade_name].keys():
                bets[venue_code][grade_name][str_dist] = {
                    "bet_count": 0,
                    "spent": 0,
                    "return": 0
                }
            venue_grade_distance = bets[venue_code][grade_name][str_dist]
            venue_grade_distance["bet_count"] += 1
            # venue_grade_distance["spent"] += self.get_bet_size(prediction.smo)
            bet_size = self.get_bet_size(prediction.smo)
            if bet_size:
                bets[venue_code][grade_name][str_dist]["spent"] += bet_size
            try:
                if participant.straight_wager.win:
                    # print(participant.straight_wager.win)
                    bets[venue_code][grade_name][str_dist]["return"] += participant.straight_wager.win
            except:
                pass

            bets[venue_code][grade_name][str_dist]
            bets[venue_code][grade_name][str_dist]["bet_count"] += 1
            # print(prediction.smo)

        self.print_report(bets)
