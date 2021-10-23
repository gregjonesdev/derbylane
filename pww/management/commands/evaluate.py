from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
import datetime

from pww.models import Prediction
from pww.utilities.weka import evaluate_all
from rawdat.models import Program, Venue, Bet, Participant, Race

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

    def analyze_object(self, prediction_obj):
        print("\t\t\t\t\t{}".format("Winnings Per $2 Bet"))
        for key in prediction_obj:
            print(key)
            print("{}\t{}\t\t{}\t\t{}\t\t{}".format("Lib SVM", "Count", "Win", "Place", "Show"))
            target_obj = prediction_obj[key]
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


    def handle(self, *args, **options):
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(days=1)).date()
        # venue_metrics = Metric.objects.filter(
        #     participant__race__chart__program__venue__code=venue_code)
        # data_row = "{} {}\t{}\t\t{}\t\t{}\t\t{}\t\t{}"

        # for program in Program.objects.filter(venue__code="WD"):
        #     print("{}".format(program.venue))
        #     print("--------------------------------------")


        # libsvm_count = {
        #     "1": 0,
        #     "2": 0,
        #     "3": 0,
        #     "4": 0,
        #     "5": 0,
        #     "6": 0,
        #     "7": 0,
        #     "8": 0
        # }

        race_predictions = {}

            # for chart in program.chart_set.all():
                # print("\n{}".format(chart.get_time_display()))
                # for race in chart.race_set.all():
        races_analyzed = Race.objects.filter(
            # chart__program__date=yesterday,
            chart__program__venue__code="WD")

        # for race in races_analyzed:
        #     print(race)
        # raise SystemExit(0)
        for race in races_analyzed:
            if race.has_predictions():
                grade_name = race.grade.name
                race_key = "{}_{}".format(race.chart.program.venue.code, grade_name)
                if not race_key in race_predictions.keys():
                    race_predictions[race_key] = {}
                # print("Race {} | {}".format(race.number, grade_name))
                # print(data_row.format(
                #     "Participant",
                #     "\t",
                #     "Finish",
                #     "LibSVM",
                #     "W",
                #     "P",
                #     "S"))
                for participant in race.participant_set.all():
                    prediction = None
                    try:
                        prediction = participant.prediction
                    except:
                        pass
                    if prediction:
                        if prediction.lib_svm:
                            if not prediction.lib_svm in race_predictions[race_key].keys():
                                race_predictions[race_key][prediction.lib_svm] = []
                            race_predictions[race_key][prediction.lib_svm].append(participant)
                            # libsvm_count[str(prediction.lib_svm)] += 1
                        # win = self.get_win_return(participant, 2)
                        # place = self.get_place_return(participant, 2)
                        # show = self.get_show_return(participant, 2)
                        # print(data_row.format(
                        #     "[{}]".format(participant.post),
                        #     participant.dog.name[:6],
                        #     "\t{}".format(participant.final),
                        #     prediction.lib_svm,
                        #     win,
                        #     place,
                        #     show))
                # print("\n")

        self.analyze_object(race_predictions)
        print("Races Analyzed: {}".format(len(races_analyzed)))
