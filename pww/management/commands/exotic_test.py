import datetime
import sys

from time import time
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from miner.utilities.constants import focused_distances, c_data, bcolors
from miner.utilities.common import get_race_key
from rawdat.models import Participant, Race
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
        parser.add_argument('--prediction', type=str)

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

        print("{}\t\t{}".format(
            scenario,
            "Superfecta"
        ))

    def evaluate_trifectas(
        self,
        testing_races,
        prediction_list,
        prediction_numbers):

        scenario = "{}-{}-{}".format(
            prediction_numbers[0],
            prediction_numbers[1],
            prediction_numbers[2])

        print("{}\t\t{}".format(
            scenario,
            "Trifecta"
        ))

    def get_quinella_return(
        self,
        testing_races,
        prediction_list,
        prediction_numbers):

        scenario = "{}-{}".format(
            prediction_numbers[0],
            prediction_numbers[1])

        print("{}\t\t{}".format(
            scenario,
            "Quienlla"
        ))
        #


        #
        #
        #
        #
        # for race in testing_races:
        #     matches_predictions = self.get_matching_participants(
        #         race,
        #         prediction_1,
        #         prediction_2,
        #         prediction_list)
        #     matches_first = matches_predictions[0]
        #     matches_second = matches_predictions[1]
        #     unique_quinellas = self.get_unique_quinellas(
        #         matches_first,
        #         matches_second)
        #     if len(unique_quinellas) > 0:
        #         for pair in unique_quinellas:
        #             print("{} - {}".format(pair[0].dog.name, pair[1].dog.name))
        #         print("---------")

        raise SystemExit(0)


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
        prediction_1,
        prediction_2,
        prediction_list):
        matches_1 = []
        matches_2 = []
        for participant in race.participant_set.all():
            try:
                str_uuid = str(participant.uuid)
                participant_prediction = prediction_list[str_uuid]
                int_pred = int(participant_prediction)
                if int_pred == prediction_1:
                    matches_1.append(participant)
                elif int_pred == prediction_2:
                    matches_2.append(participant)
            except:
                pass
        return [matches_1, matches_2]


    def get_unique_quinellas(self, matches_first, matches_second):
        unique_quinellas = []
        i = 0
        while i < len(matches_first):
            first = matches_first[i]
            j = 0
            while j < len(matches_second):
                second = matches_second[j]
                if not first == second:
                    if not (first, second) in unique_quinellas:
                        if not (second, first) in unique_quinellas:
                            unique_quinellas.append((first, second))
                j += 1
            i += 1

        return unique_quinellas


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



    def print_returns(self, testing_races, prediction_list, c, race_key, cutoff_date, loader):
        prediction_numbers = [0, 0, 0, 0]
        highest_number = 5
        while prediction_numbers[0] < highest_number:
            prediction_numbers[1] = 0
            while prediction_numbers[1] < highest_number:
                self.get_quinella_return(
                    testing_races,
                    prediction_list,
                    prediction_numbers)
                prediction_numbers[2] = 0
                while prediction_numbers[2] < highest_number:
                    prediction_numbers[3] = 0
                    self.evaluate_trifectas(
                        testing_races,
                        prediction_list,
                        prediction_numbers)
                    while prediction_numbers[3] < highest_number:
                        # self.evaluate_superfectas(
                        #     testing_races,
                        #     prediction_list,
                        #     prediction_numbers)
                        prediction_numbers[3] += 1
                    prediction_numbers[2] += 1
                prediction_numbers[1] += 1
            prediction_numbers[0] += 1





        # uuid_line_index = get_uuid_line_index(testing_arff)
        # testing_data = build_scheduled_data(testing_arff)
        # prediction_list = get_prediction_list(model, testing_data, uuid_line_index)
        #
        # for uuid in prediction_list.keys():
        #
        #     if int(prediction_list[uuid]) == int(prediction):
        #         bet_count += 1
        #         participant = Participant.objects.get(uuid=uuid)
        #         win_returns += self.get_win_return(participant)
        #         place_returns += self.get_place_return(participant)
        #         show_returns += self.get_show_return(participant)
        #
        # if bet_count > 0:
        #     average_returns = [
        #         win_returns/bet_count,
        #         place_returns/bet_count,
        #         show_returns/bet_count]
        #     max_return = max(average_returns)
        #     print(table_string.format(
        #         c,
        #         self.get_formatting(max_return, average_returns[0]),
        #         self.get_formatting(max_return, average_returns[1]),
        #         self.get_formatting(max_return, average_returns[2]),
        #         bet_count,
        #         "\t{}".format(round(max_return*bet_count, 3))))



    def handle(self, *args, **options):
        venue_code = "TS"
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
        c = 0.01
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
            print("\nc = {}\n".format(c))
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

        print("\nCompleted Analysis in {}:{}:{}".format(
        self.two_digitizer(int(hours)),
        self.two_digitizer(int(minutes)),
        self.two_digitizer(int(seconds))))
