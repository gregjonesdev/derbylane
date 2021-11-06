import datetime
import sys

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from pww.models import Prediction
from pww.utilities.weka import evaluate_all
from rawdat.models import Program, Venue, Bet, Participant, Race

from miner.utilities.constants import (
    focused_distances,
    focused_grades)

interval = 0.25
start = 1.0
end = 8.0

table_string = "{}\t\t{}\t\t{}\t\t{}\t\t{}"

class Command(BaseCommand):

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

    def get_value(self, wager):
        if wager:
            return wager
        else:
            return 0

    def get_bet_winnings(self, participant_list):
        bet_winnings = {
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
                bet_winnings["win"] += self.get_value(straight_wager.win)
                bet_winnings["place"] += self.get_value(straight_wager.place)
                bet_winnings["show"] += self.get_value(straight_wager.show)
        return bet_winnings

    def get_winnings_per_bet(self, money, bet_count):
        if bet_count > 0:
            amount = money/bet_count
            if amount > 0:
                return "${}".format(round(amount, 2))
        return "-----"




    def analyze_object(self, prediction_obj, model_name):
        print("\nAnalysis of {} model".format(model_name))
        print("\t\t\t\t\t{}".format("Winnings Per $2 Bet"))
        for key in prediction_obj:
            print(key)
            print("{}\t\t{}\t\t{}\t\t{}\t\t{}".format(" ", "Count", "Win", "Place", "Show"))
            target_obj = prediction_obj[key]
            counts = []
            for subkey in sorted(prediction_obj[key].keys()):
                participant_list = target_obj[subkey]
                bet_winnings = self.get_bet_winnings(participant_list)
                bet_count = len(participant_list)
                print("{}\t\t{}\t\t{}\t\t{}\t\t{}".format(
                    subkey,
                    bet_count,
                    self.get_winnings_per_bet(bet_winnings["win"], bet_count),
                    self.get_winnings_per_bet(bet_winnings["place"], bet_count),
                    self.get_winnings_per_bet(bet_winnings["show"], bet_count)))
            print("\n")


    def output(self, predictions):
        for each in predictions.keys():
            print("\n{}".format(each))

            for interval in predictions[each].keys():
                range = self.get_range(interval)
                print(table_string.format(
                    "{} - {}".format(range[0], range[1]),
                    "# bets",
                    "W",
                    "P",
                    "S"
                ))

    def get_range(self, nominal):
        return [float(nominal), float(nominal) + interval]


    # def analyze_race()
    def build_beginning_object(self):
        object = {}
        i = start
        while i < end:
            object[str(i)] = {
                "win": [],
                "place": [],
                "show":[]
            }
            i += interval
        return object

    def find_range_start(self):
        target = 0.99
        for i in [0, 0.25, 0.5, 0.75]:
            if target-i < interval and target >= i:
                print(i)

    def handle(self, *args, **options):
        self.find_range_start()
        raise SystemExit(0)
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(days=1)).date()
        start_date = (today - datetime.timedelta(days=60)).date()

        venue_code = "WD"
        race_predictions = {}

        for grade_name in focused_grades[venue_code]:
            graded_races = Race.objects.filter(
                chart__program__date__gte=start_date,
                chart__program__venue__code=venue_code,
                grade__name=grade_name)

            for race in graded_races:
                if race.is_complete():
                    race_key = "{}_{}".format(venue_code, grade_name)
                    if not race_key in race_predictions.keys():
                        race_predictions[race_key] = self.build_beginning_object()
                        for participant in race.participant_set.all():
                            prediction = None
                            try:
                                prediction = participant.prediction
                            except:
                                pass
                            if prediction and prediction.smo:
                                current_prediction = prediction.smo
                                print(current_prediction)


        raise SystemExit(0)

        self.output(race_predictions)

        #
        # for race in races_analyzed:
        #     if race.has_predictions():
        #         grade_name = race.grade.name
        #         race_key = "{}_{}".format(venue_code, grade_name)
        #         if not race_key in race_predictions.keys():
        #             race_predictions[race_key] = {}
        #         for participant in race.participant_set.all():
        #             prediction = None
        #             try:
        #                 prediction = participant.prediction
        #             except:
        #                 pass
        #             if prediction:
        #                 if model_name == "smo":
        #                     current_prediction = prediction.smo
        #                 elif model_name == "libsvm":
        #                     current_prediction = prediction.lib_svm
        #                 elif model_name == "j48":
        #                     current_prediction = prediction.j48
        #                 if current_prediction:
        #                     if not current_prediction in race_predictions[race_key].keys():
        #                         race_predictions[race_key][current_prediction] = []
        #                     race_predictions[race_key][current_prediction].append(participant)
        #     self.analyze_object(race_predictions, model_name)
        #     print("Races Analyzed: {}\n".format(len(races_analyzed)))
