from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
import datetime

from pww.models import Prediction
from pww.utilities.weka import evaluate_all
from rawdat.models import Program, Venue, Bet, Participant

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

        target_day = yesterday
        arff_list = []
        # venue_metrics = Metric.objects.filter(
        #     participant__race__chart__program__venue__code=venue_code)
        data_row = "[{}] {}\t{}\t{}"

        column_names = [
            "Post",
            "Dog Name",
            "Finish",
            "LibSVM"
        ]


        for program in Program.objects.filter(date=yesterday, venue__code="WD"):
            print("{}".format(program.venue))
            print("--------------------------------------")
            for chart in program.chart_set.all():
                print("\n{}".format(chart.get_time_display()))
                for race in chart.race_set.all():
                    if race.has_predictions():
                        print("Race {}".format(race.number))
                        print(race.has_predictions())
                        for participant in race.participant_set.all():
                            try:
                                # print(participant.prediction)
                                print(data_row.format(
                                    participant.post,
                                    participant.dog.name[:6],
                                    participant.final,
                                    participant.prediction.lib_svm))
                            except:
                                pass

                        print("\n")






        # evaluate_all(arff_list, venue.code, "A")
