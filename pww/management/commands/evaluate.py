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

    def evaluate_bet_cutoffs():
        pass

    def get_value(self, wager):
        if wager:
            return wager
        else:
            return 0


    def get_bet_returns(self, participant_list):
        bet_returns = {
            "win": 0,
            "place": 0,
            "show": 0
        }
        for participant in participant_list:
            straight_wager = None
            try:
                straight_wager = participant.straight_wager
            except:
                pass
            if straight_wager:
                bet_returns["win"] += self.get_value(straight_wager.win)
                bet_returns["place"] += self.get_value(straight_wager.place)
                bet_returns["show"] += self.get_value(straight_wager.show)
        return bet_returns

    def get_return_per_bet(self, money, bet_count):
        if bet_count > 0:
            return "${}".format(round(money/bet_count, 2))
        else:
            return "$0"

    def analyze_object(self, prediction_obj):
        print("\t\t\t\t\t{}".format("Return Per Bet"))
        for key in prediction_obj:
            print(key)
            print("{}\t{}\t\t{}\t\t{}\t\t{}".format("Prediction", "Count", "Win", "Place", "Show"))
            target_obj = prediction_obj[key]
            for subkey in sorted(prediction_obj[key].keys()):
                participant_list = target_obj[subkey]
                bet_returns = self.get_bet_returns(participant_list)
                bet_count = len(participant_list)
                print("{}\t\t{}\t\t{}\t\t{}\t\t{}".format(
                    subkey,
                    bet_count,
                    self.get_return_per_bet(bet_returns["win"], bet_count),
                    self.get_return_per_bet(bet_returns["place"], bet_count),
                    self.get_return_per_bet(bet_returns["show"], bet_count)))
            print("\n")


    def handle(self, *args, **options):
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(days=1)).date()

        target_day = yesterday
        arff_list = []
        # venue_metrics = Metric.objects.filter(
        #     participant__race__chart__program__venue__code=venue_code)
        data_row = "{} {}\t{}\t\t{}\t\t{}\t\t{}\t\t{}"

        for program in Program.objects.filter(date=yesterday, venue__code="WD"):
            print("{}".format(program.venue))
            print("--------------------------------------")


            libsvm_count = {
                "1": 0,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0,
                "6": 0,
                "7": 0,
                "8": 0
            }

            empty_obj = {
                "1": [],
                "2": [],
                "3": [],
                "4": [],
                "5": [],
                "6": [],
                "7": [],
                "8": []
            }

            total_predicitions = 0

            prediction_obj = {}






            race_predictions = {}








            for chart in program.chart_set.all():
                print("\n{}".format(chart.get_time_display()))
                for race in chart.race_set.all():
                    if race.has_predictions():
                        grade_name = race.grade.name
                        race_key = "{}_{}".format(program.venue.code, grade_name)
                        if not race_key in race_predictions.keys():
                            race_predictions[race_key] = {}
                        print("Race {} | {}".format(race.number, grade_name))
                        print(data_row.format(
                            "Participant",
                            "\t",
                            "Finish",
                            "LibSVM",
                            "W",
                            "P",
                            "S"))
                        for participant in race.participant_set.all():
                            prediction = None
                            try:
                                prediction = participant.prediction
                            except:
                                pass
                            if prediction:
                                if prediction.lib_svm:
                                    total_predicitions += 1
                                    if not prediction.lib_svm in race_predictions[race_key].keys():
                                        race_predictions[race_key][prediction.lib_svm] = []
                                    race_predictions[race_key][prediction.lib_svm].append(participant)
                                    libsvm_count[str(prediction.lib_svm)] += 1
                                win = self.get_win_return(participant, 2)
                                place = self.get_place_return(participant, 2)
                                show = self.get_show_return(participant, 2)
                                print(data_row.format(
                                    "[{}]".format(participant.post),
                                    participant.dog.name[:6],
                                    "\t{}".format(participant.final),
                                    prediction.lib_svm,
                                    win,
                                    place,
                                    show))
                        print("\n")

            # if total_predicitions > 0:
            #     print("LibSVM Breakdown")
            #     for each in libsvm_count:
            #         current_count = libsvm_count[each]
            #         print("{}\t\t\t{}\t\t{}%".format(each, current_count, int(current_count*100/total_predicitions)))
            #
            #
            self.analyze_object(race_predictions)



        # evaluate_all(arff_list, venue.code, "A")
