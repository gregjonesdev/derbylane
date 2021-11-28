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

    def evaluate_predicions(
        self,
        testing_races,
        prediction_list,
        prediction_1,
        prediction_2):
        print("Evaluate predcitions")
        print("{} - {}".format(prediction_1, prediction_2))
        print(len(testing_races))
        print(len(prediction_list))

                # testing_arff = get_testing_arff(
                #     race_key,
                #     testing_metrics,
                #     is_nominal)
        # testing_metrics = all_metrics.filter(
        #     participant__race__chart__program__date__gt=cutoff_date)
        # testing_arff = get_testing_arff(
        #     race_key,
        #     testing_metrics,
        #     is_nominal)

        # prediction_list = get_prediction_list(model, testing_data, uuid_line_index)

        # uuid_line_index = get_uuid_line_index(testing_arff)
        #
        for race in testing_races:
            print(self.get_matching_participants(race, prediction_1, prediction_list))
        #     # get race predictions
        #
        #
        #     for participant in race.participant_set.all():
        #         print(participant.uuid in prediction_list.keys())


    def get_testing_metrics(self, testing_races):
        testing_metrics = []
        for race in testing_races:
            for participant in race.participant_set.all():
                try:
                    testing_metrics.append(participant.metric)
                except:
                    pass
        return testing_metrics

    def get_matching_participants(self, race, prediction, prediction_list):
        matching_participants = []
        for participant in race.participant_set.all():
            try:
                str_uuid = str(participant.uuid)
                participant_prediction = prediction_list[str_uuid]
                if int(participant_prediction) == prediction:
                    matching_participants.append(participant)
            except:
                pass
        return matching_participants


    def get_unique_quinellas(self, matches_first, matches_second):
        print("get unique quinells:")
        matches_first = [1,3,5]
        matches_second = [1,3,5]
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
        print(unique_quinellas)



    def print_returns(self, testing_races, prediction_list, c, race_key, cutoff_date, loader):
        prediction_1 = 0
        while prediction_1 < 5:
            prediction_2 = 0
            while prediction_2 < 5:
                self.evaluate_predicions(
                    testing_races,
                    prediction_list,
                    prediction_1,
                    prediction_2)
                prediction_2 += 1
            prediction_1 += 1





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
