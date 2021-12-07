import datetime
import sys

from time import time
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from miner.utilities.constants import focused_distances, c_data, bcolors
from miner.utilities.common import get_race_key
from rawdat.models import (
    Participant,
    Race,
    Quiniela,
    Exacta,
    Trifecta,
    Superfecta)
from pww.utilities.ultraweka import (
    create_model,
    build_scheduled_data,
    get_uuid_line_index,
    get_prediction_list,
    get_metrics)
from weka.classifiers import Classifier
import weka.core.converters as conv
import weka.core.jvm as jvm
import weka.core.serialization as serialization
from pww.utilities.arff import get_training_arff, get_testing_arff, get_arff_filename


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str)
        parser.add_argument('--grade', type=str)
        # parser.add_argument('--prediction', type=str)

    def get_race_predictions(self, race):
        pass

    def evaluate_superfectas(
        self,
        testing_races,
        prediction_list,
        prediction_numbers):

        scenario = "{}-{}-{}-{}".format(
            prediction_numbers[0],
            prediction_numbers[1],
            prediction_numbers[2],
            prediction_numbers[3])


    def evaluate_trifectas(
        self,
        testing_races,
        prediction_list,
        prediction_numbers):

        scenario = "{}-{}-{}".format(
            prediction_numbers[0],
            prediction_numbers[1],
            prediction_numbers[2])


    def get_quiniela_return(
        self,
        testing_races,
        prediction_list,
        prediction_numbers):

        bet_winnings = []

        for race in testing_races:
            matches_predictions = self.get_matching_participants(
                race,
                prediction_numbers,
                prediction_list)
            matches_first = matches_predictions[0]
            matches_second = matches_predictions[1]
            unique_quinielas = self.get_unique_quinielas(
                matches_first,
                matches_second)
            for pair in unique_quinielas:
                bet_winnings.append(
                    self.get_quiniela_winnings(pair[0], pair[1]))

        return bet_winnings

    def get_exacta_return(
        self,
        testing_races,
        prediction_list,
        prediction_numbers):

        bet_winnings = []

        for race in testing_races:
            matches_predictions = self.get_matching_participants(
                race,
                prediction_numbers,
                prediction_list)
            matches_first = matches_predictions[0]
            matches_second = matches_predictions[1]
            unique_exactas = self.get_unique_exactas(
                matches_first,
                matches_second)
            for pair in unique_exactas:
                bet_winnings.append(
                    self.get_exacta_winnings(pair[0], pair[1]))

        return bet_winnings

    def get_trifecta_return(
        self,
        testing_races,
        prediction_list,
        prediction_numbers):

        bet_winnings = []

        for race in testing_races:
            matches_predictions = self.get_matching_participants(
                race,
                prediction_numbers,
                prediction_list)
            matches_first = matches_predictions[0]
            matches_second = matches_predictions[1]
            matches_third = matches_predictions[2]
            unique_trifectas = self.get_unique_trifectas(
                matches_first,
                matches_second,
                matches_third)
            for set in unique_trifectas:
                bet_winnings.append(
                    self.get_trifecta_winnings(set[0], set[1], set[2]))

        return bet_winnings

    def get_average_return(self, bet_winnings):
        if len(bet_winnings) > 0:
            return float(round(sum(bet_winnings)/len(bet_winnings), 2))
        else:
            return 0

    def get_quiniela_winnings(self, participant_1, participant_2):
        quienla = None
        try:
            quienla = Quiniela.objects.get(
                left=participant_1,
                right=participant_2
            )
        except ObjectDoesNotExist:
            try:
                quienla = Quiniela.objects.get(
                    left=participant_2,
                    right=participant_1
                )
            except ObjectDoesNotExist:
                pass
        if quienla:
            return quienla.payout
        return 0

    def get_exacta_winnings(self, participant_1, participant_2):
        exacta = None
        try:
            exacta = Exacta.objects.get(
                win=participant_1,
                place=participant_2
            )
        except ObjectDoesNotExist:
            pass
        if exacta:
            return exacta.payout
        return 0

    def get_trifecta_winnings(self, participant_1, participant_2, participant_3):
        trifecta = None
        try:
            trifecta = Trifecta.objects.get(
                win=participant_1,
                place=participant_2,
                show=participant_3
            )
        except ObjectDoesNotExist:
            pass
        if trifecta:
            return trifecta.payout
        return 0

    def get_testing_metrics(self, testing_races):
        testing_metrics = []
        for race in testing_races:
            for participant in race.participant_set.all():
                try:
                    testing_metrics.append(participant.metric)
                except:
                    pass
        return testing_metrics

    def get_matching_participants(
        self,
        race,
        predictions,
        prediction_list):
        matches_1 = []
        matches_2 = []
        matches_3 = []
        matches_4 = []
        for participant in race.participant_set.all():
            try:
                str_uuid = str(participant.uuid)
                participant_prediction = prediction_list[str_uuid]
                int_pred = int(participant_prediction)
                if int_pred == predictions[0]:
                    matches_1.append(participant)
                elif int_pred == predictions[1]:
                    matches_2.append(participant)
                elif int_pred == predictions[2]:
                    matches_3.append(participant)
                elif int_pred == predictions[3]:
                    matches_4.append(participant)
            except:
                pass
        return [matches_1, matches_2, matches_3, matches_4]


    def get_unique_quinielas(self, matches_first, matches_second):
        unique_quinielas = []
        i = 0
        while i < len(matches_first):
            first = matches_first[i]
            j = 0
            while j < len(matches_second):
                second = matches_second[j]
                if not first == second:
                    if not (first, second) in unique_quinielas:
                        if not (second, first) in unique_quinielas:
                            unique_quinielas.append((first, second))
                j += 1
            i += 1

        return unique_quinielas


    def get_unique_exactas(self, matches_first, matches_second):
        unique_exactas = []
        i = 0
        while i < len(matches_first):
            first = matches_first[i]
            j = 0
            while j < len(matches_second):
                second = matches_second[j]
                if not first == second:
                    if not (first, second) in unique_exactas:
                        unique_exactas.append((first, second))
                j += 1
            i += 1

        return unique_exactas

    def get_unique_trifectas(self, matches_first, matches_second, matches_third):
        unique_trifectas = []
        i = 0
        while i < len(matches_first):
            first = matches_first[i]
            j = 0
            while j < len(matches_second):
                second = matches_second[j]
                k = 0
                while k < len(matches_third):
                    third = matches_third[k]
                    if not (
                        first == second or
                        first == third or
                        second == third):
                        if not (first, second, third) in unique_trifectas:
                            unique_trifectas.append((first, second, third))
                    k += 1
                j += 1
            i += 1

        return unique_trifectas

    def get_potential(self, average_return, bet_winnings):
        if average_return > 2:
            return average_return*len(bet_winnings)
        else:
            return 0

    def get_optimal_quiniela(
        self,
        optimal_quiniela,
        testing_races,
        prediction_list,
        prediction_numbers):
        current_quiniela = self.get_quiniela_return(
            testing_races,
            prediction_list,
            prediction_numbers)
        average_return = self.get_average_return(current_quiniela)
        if average_return > 2:
            current_potential = self.get_potential(average_return, current_quiniela)
            if current_potential > optimal_quiniela["potential"]:
                return {
                    "scenario": "{}-{}".format(prediction_numbers[0], prediction_numbers[1]),
                    "average_return": average_return,
                    "potential": current_potential,
                }
        return optimal_quiniela

    def get_optimal_exacta(
        self,
        optimal_exacta,
        testing_races,
        prediction_list,
        prediction_numbers):
        current_exacta = self.get_exacta_return(
            testing_races,
            prediction_list,
            prediction_numbers)
        average_return = self.get_average_return(current_exacta)
        if average_return > 2:
            current_potential = self.get_potential(average_return, current_exacta)
            if current_potential > optimal_exacta["potential"]:
                return {
                    "scenario": "{}-{}".format(prediction_numbers[0], prediction_numbers[1]),
                    "average_return": average_return,
                    "potential": int(current_potential),
                }
        return optimal_exacta

    def get_optimal_trifecta(
        self,
        optimal_trifecta,
        testing_races,
        prediction_list,
        prediction_numbers):
        current_trifecta = self.get_trifecta_return(
            testing_races,
            prediction_list,
            prediction_numbers)
        average_return = self.get_average_return(current_trifecta)
        if average_return > 2:
            current_potential = self.get_potential(average_return, current_trifecta)
            if current_potential > optimal_trifecta["potential"]:
                return {
                    "scenario": "{}-{}-{}".format(prediction_numbers[0], prediction_numbers[1], prediction_numbers[2]),
                    "average_return": average_return,
                    "potential": int(current_potential),
                }
        return optimal_trifecta

    def print_optimal_bet(self, optimal_bet, bet_name):
        if optimal_bet["average_return"] > 0:
            print("Optimal {}:\t{}\t{}\t{}".format(
                bet_name,
                optimal_bet["scenario"],
                optimal_bet["average_return"],
                optimal_bet["potential"]))



    def print_returns(self, testing_races, prediction_list, c, race_key, cutoff_date, loader):
        prediction_numbers = [0, 0, 0, 0]
        highest_number = 5
        optimal_quiniela = {
            "scenario": "",
            "average_return": 0,
            "potential": 0,
        }
        optimal_exacta = {
            "scenario": "",
            "average_return": 0,
            "potential": 0,
        }
        optimal_trifecta = {
            "scenario": "",
            "average_return": 0,
            "potential": 0,
        }
        while prediction_numbers[0] < highest_number:
            prediction_numbers[1] = 0
            while prediction_numbers[1] < highest_number:
                optimal_quiniela = self.get_optimal_quiniela(
                    optimal_quiniela,
                    testing_races,
                    prediction_list,
                    prediction_numbers)
                optimal_exacta = self.get_optimal_exacta(
                    optimal_exacta,
                    testing_races,
                    prediction_list,
                    prediction_numbers)
                prediction_numbers[2] = 0
                while prediction_numbers[2] < highest_number:
                    optimal_trifecta = self.get_optimal_trifecta(
                        optimal_trifecta,
                        testing_races,
                        prediction_list,
                        prediction_numbers)
                    # prediction_numbers[3] = 0
                #     while prediction_numbers[3] < highest_number:
                #         self.evaluate_superfectas(
                #             testing_races,
                #             prediction_list,
                #             prediction_numbers)
                #         prediction_numbers[3] += 1
                    prediction_numbers[2] += 1
                prediction_numbers[1] += 1
            prediction_numbers[0] += 1

        self.print_optimal_bet(optimal_quiniela, "Quiniela")
        self.print_optimal_bet(optimal_exacta, "Exacta")
        self.print_optimal_bet(optimal_trifecta, "Trifecta")


    def handle(self, *args, **options):
        venue_code = "WD"
        grade_name = sys.argv[5]
        distance = focused_distances[venue_code][0]
        today = datetime.datetime.now()
        cutoff_date = (today - datetime.timedelta(days=49)).date()
        start_time = time()
        all_metrics = get_metrics(
            venue_code,
            distance,
            grade_name)
        training_metrics = all_metrics.filter(
            participant__race__chart__program__date__lte=cutoff_date)
        testing_races = Race.objects.filter(
            chart__program__date__gt=cutoff_date)
        race_key = get_race_key(venue_code, distance, grade_name)
        is_nominal = False
        training_arff = get_training_arff(
            race_key,
            training_metrics,
            is_nominal)
        testing_metrics = self.get_testing_metrics(testing_races)
        testing_arff = get_testing_arff(
            race_key,
            testing_metrics,
            is_nominal)
        max_return = 0
        classifier_name = sys.argv[3]


        jvm.start(packages=True, max_heap_size="5028m")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")

        testing_data = build_scheduled_data(testing_arff)
        uuid_line_index = get_uuid_line_index(testing_arff)
        # prediction_list = get_prediction_list(model, testing_data, uuid_line_index)

        c_start = c_data[classifier_name]["c_start"]
        c_stop = c_data[classifier_name]["c_stop"]
        interval = c_data[classifier_name]["interval"]


        # print("\n\n{} Prediction Accuracy vs Confidence Factor".format(
        #     classifier_name.upper()))
        # print("{} {} {}\n".format(venue_code, grade_name, distance))
        # print("Dogs Predicted to Finish {}".format(pred_format[prediction]))
        # print(table_string.format(
        #     "C",
        #     "Win",
        #     "Place",
        #     "Show",
        #     "Bet Count",
        #     "Potential"))
        # testing_data = build_scheduled_data(testing_arff)
        c = c_start
        while c <= c_stop:
            c = round(c, 2)
            print("\nc = {}".format(c))
            model_name = create_model(training_arff, classifier_name, str(c), race_key, loader)
            model = Classifier(jobject=serialization.read(model_name))
            prediction_list = get_prediction_list(model, testing_data, uuid_line_index)
            self.print_returns(testing_races, prediction_list, str(c), race_key, cutoff_date, loader)
            c = round(c + interval, 2)

        jvm.stop()
        end_time = time()
        seconds_elapsed = end_time - start_time

        hours, rest = divmod(seconds_elapsed, 3600)
        minutes, seconds = divmod(rest, 60)

        print("\nAll metrics: {}".format(len(all_metrics)))
        print("Training metrics: {}".format(len(training_metrics)))

        # print("\nCompleted Analysis in {}:{}:{}".format(
        # self.two_digitizer(int(hours)),
        # self.two_digitizer(int(minutes)),
        # self.two_digitizer(int(seconds))))
