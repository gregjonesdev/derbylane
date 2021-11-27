import datetime
import sys

from time import time
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from miner.utilities.urls import arff_directory
from miner.utilities.constants import focused_distances, c_data, bcolors
from miner.utilities.common import get_race_key
from rawdat.models import Participant
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




    def get_formatting(self, max, value):
        formatting = ""
        if value > 2.00:
            formatting += bcolors.OKGREEN
            formatting += bcolors.BOLD
        return formatting + "${:.2f}".format(value) + bcolors.ENDC


    def evaluate_predicions(self, prediction_1, prediction_2):
        pass




    def print_returns(self, model_name, testing_arff, c, race_key, loader, prediction):
        # print(model_name)
        model = Classifier(jobject=serialization.read(model_name))
        # print(type(testing_arff))
        uuid_line_index = get_uuid_line_index(testing_arff)
        # print(uuid_line_index)
        testing_data = build_scheduled_data(testing_arff)
        # model.build_classifier(testing_data)
        prediction_list = get_prediction_list(model, testing_data, uuid_line_index)

        for uuid in prediction_list.keys():

            if int(prediction_list[uuid]) == int(prediction):
                bet_count += 1
                participant = Participant.objects.get(uuid=uuid)
                win_returns += self.get_win_return(participant)
                place_returns += self.get_place_return(participant)
                show_returns += self.get_show_return(participant)

        if bet_count > 0:
            average_returns = [
                win_returns/bet_count,
                place_returns/bet_count,
                show_returns/bet_count]
            max_return = max(average_returns)
            print(table_string.format(
                c,
                self.get_formatting(max_return, average_returns[0]),
                self.get_formatting(max_return, average_returns[1]),
                self.get_formatting(max_return, average_returns[2]),
                bet_count,
                "\t{}".format(round(max_return*bet_count, 3))))



    def handle(self, *args, **options):
        venue_code = "TS"
        grade_name = sys.argv[5]
        distance = focused_distances[venue_code][0]
        today = datetime.datetime.now()
        cutoff_date = (today - datetime.timedelta(days=49)).date()
        # training_cutoff = (today - datetime.timedelta(days=7)).date()
        start_time = time()
        all_metrics = get_metrics(venue_code, distance, grade_name)
        training_metrics = all_metrics.filter(participant__race__chart__program__date__lte=cutoff_date)
        testing_metrics = all_metrics.filter(participant__race__chart__program__date__gt=cutoff_date)
        race_key = get_race_key(venue_code, distance, grade_name)


        training_arff_filename = get_arff_filename("train", race_key)
        testing_arff_filename = get_arff_filename("test", race_key)
        is_nominal = False
        # print("training metrics: {}".format(len(training_metrics)))
        training_arff = get_training_arff(
            race_key,
            training_metrics,
            is_nominal)
        testing_arff = get_testing_arff(
            race_key,
            training_metrics,
            is_nominal)


        print("here")
        raise SystemExit(0)
        c = 0.01
        max_return = 0


        jvm.start(packages=True, max_heap_size="5028m")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")
        classifier_name = sys.argv[3]

        prediction = sys.argv[7]

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
        c = c_start
        while c <= c_stop:
            c = round(c, 2)
            model_name = create_model(training_arff, classifier_name, str(c), race_key, loader)
            self.print_returns(model_name, testing_arff, str(c), race_key, loader, prediction)
            c = round(c + interval, 2)

        jvm.stop()
        end_time = time()
        seconds_elapsed = end_time - start_time

        hours, rest = divmod(seconds_elapsed, 3600)
        minutes, seconds = divmod(rest, 60)

        print("\nAll metrics: {}".format(len(all_metrics)))
        print("Training metrics: {}".format(len(training_metrics)))
        print("Test metrics: {}".format(len(testing_metrics)))

        print("\nCompleted Analysis in {}:{}:{}".format(
        self.two_digitizer(int(hours)),
        self.two_digitizer(int(minutes)),
        self.two_digitizer(int(seconds))))
