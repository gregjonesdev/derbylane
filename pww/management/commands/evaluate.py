from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
import datetime

from pww.models import Prediction
from rawdat.models import Program

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
            list_ppb = []
            for grade_name in bets[venue_code].keys():
                for distance in bets[venue_code][grade_name].keys():
                    vgd = bets[venue_code][grade_name][distance]
                    ret = vgd["return"]
                    bet = vgd["bet_count"]
                    spent = vgd["spent"]
                    try:
                        ppb = (float(ret)-float(spent))/bet
                        list_ppb.append(ppb)
                    except:
                        ppb = "N/A"
                    print("{}\t{}\t{}\t\t{}\t\t{}\t\t{}\t\t{}".format(
                        venue_code,
                        grade_name,
                        distance,
                        bet,
                        spent,
                        str(round(ret, 2)),
                        str(round(ppb, 2))
                    ))
        print("\t\t\t\t\t\t\t\tAverage:\t{}".format(str(round(sum(list_ppb)/len(list_ppb), 2))))

    def get_bet_size(self, value):

        if value < 3:
            return 2.00
        # elif value <2:
        #     return 2.00
        # elif value <3:
        #     return 2.00
        else:
            return None

    def get_win_return(self, participant, bet_size):
        try:
            return (bet_size/2)*float(participant.straight_wager.win)
        except:
            return 0

    def get_place_return(self, participant, bet_size):
        try:
            return (bet_size/2)*float(participant.straight_wager.place)
        except:
            return 0

    def get_show_return(self, participant, bet_size):
        try:
            return (bet_size/2)*float(participant.straight_wager.show)
        except:
            return 0


    def handle(self, *args, **options):
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(days=1)).date()
        print(yesterday)
        venue_results = {}
        initial_obj = {
            "bets": 0,
            "win": 0,
            "place": 0,
            "show": 0
        }
        bet_size = 2.0
        for program in Program.objects.filter(date=yesterday):
            venue_code = program.venue.code
            if not venue_code in venue_results.keys():
                venue_results[venue_code] = {}
            for chart in program.chart_set.all():
                for race in chart.race_set.all():
                    grade_name = race.grade.name
                    if not grade_name in venue_results[venue_code].keys():
                        venue_results[venue_code][grade_name] = initial_obj
                    for participant in race.participant_set.all():
                        try:
                            if int(participant.prediction.smo_reg) == 0:
                                print(participant.prediction.smo_reg)
                                graded = venue_results[venue_code][grade_name]
                                graded["bets"] += 1
                                graded["win"] += (
                                    self.get_win_return(participant, bet_size))
                                graded["place"] += (
                                    self.get_place_return(participant, bet_size))
                                graded["show"] += (
                                    self.get_show_return(participant, bet_size))

                        except:
                            pass

        print(venue_results)




    # def handle(self, *args, **options):
    #     print("Bet Scheme: $2 to place on an dog predict < 3")
    #     bets = {}
    #     for prediction in Prediction.objects.filter(
    #         smo__isnull=False,
    #         participant__final__isnull=False):
    #         # print(self.get_bet_size(prediction.smo))
    #         participant = prediction.participant
    #         race = participant.race
    #         grade_name = race.grade.name
    #         distance = race.distance
    #         venue_code = race.chart.program.venue.code
    #
    #         if not venue_code in bets.keys():
    #             bets[venue_code] = {}
    #         if not grade_name in bets[venue_code].keys():
    #             bets[venue_code][grade_name] = {}
    #         str_dist = str(distance)
    #         if not str_dist in bets[venue_code][grade_name].keys():
    #             bets[venue_code][grade_name][str_dist] = {
    #                 "bet_count": 0,
    #                 "spent": 0,
    #                 "return": 0
    #             }
    #         vgd = bets[venue_code][grade_name][str_dist]
    #         bet_size = self.get_bet_size(prediction.smo)
    #         if bet_size:
    #             vgd["bet_count"] += 1
    #             vgd["spent"] += bet_size
    #             # vgd["return"] += self.get_win_return(participant, bet_size)
    #             vgd["return"] += self.get_place_return(participant, bet_size)
    #             # vgd["return"] += self.get_show_return(participant, bet_size)
    #         # print(prediction.smo)
    #
    #     self.print_report(bets)
