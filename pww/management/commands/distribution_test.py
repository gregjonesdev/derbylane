import datetime
import sys

from time import time
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from miner.utilities.urls import arff_directory
from miner.utilities.constants import focused_distances
from miner.utilities.common import get_race_key
from rawdat.models import Participant
from pww.models import TestPrediction, Metric
from pww.utilities.ultraweka import (
    create_model,
    get_metrics,
    build_scheduled_data,
    get_uuid_line_index,
    get_prediction_list)
from weka.classifiers import Classifier
import weka.core.converters as conv
import weka.core.jvm as jvm
import weka.core.serialization as serialization
from pww.utilities.arff import create_arff, get_training_arff, get_testing_arff
table_string = "{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


pred_format = {
    "0": "0",
    "1": "1st",
    "2": "2nd",
    "3": "3rd",
    "4": "4th",
    "5": "5th",
    "6": "6th",
    "7": "7th",
    "8": "8th"
}



class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str)
        parser.add_argument('--grade', type=str)
        parser.add_argument('--prediction', type=str)


    def two_digitizer(self, integer):
        if integer < 10:
            return "0{}".format(integer)
        else:
            return integer

    def get_formatting(self, max, value):
        formatting = ""
        if value > 2.00:
            formatting += bcolors.OKGREEN
            formatting += bcolors.BOLD
        return formatting + "${:.2f}".format(value) + bcolors.ENDC


    def save_prediction(self, participant_uuid, smo_prediction, c):
        # just keep it all in local memory
        c = float(c)
        try:
            prediction = TestPrediction.objects.get(
                participant_id=participant_uuid,
                c=c)
        except ObjectDoesNotExist:
            new_prediction = TestPrediction(
                participant_id=participant_uuid,
                c=c)
            new_prediction.set_fields_to_base()
            prediction = new_prediction
        prediction.smo = smo_prediction
        prediction.save()


    def get_win_return(self, participant):
        try:
            return float(participant.straight_wager.win)
        except:
            return 0

    def get_place_return(self, participant):
        try:
            return float(participant.straight_wager.place)
        except:
            return 0

    def get_show_return(self, participant):
        try:
            return float(participant.straight_wager.show)
        except:
            return 0


    def print_returns(self, prediction_list, c, race_key, loader, prediction):
        # print(model_name)

        # print(uuid_line_index)

        win_returns = 0
        place_returns = 0
        show_returns = 0
        bet_count = 0
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
            if max_return > 2.00:
                potential = round(max_return*bet_count, 3)
            else:
                potential = ""
            print(table_string.format(
                c,
                self.get_formatting(max_return, average_returns[0]),
                self.get_formatting(max_return, average_returns[1]),
                self.get_formatting(max_return, average_returns[2]),
                bet_count,
                "\t{}".format(potential)))




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
        testing_metrics = all_metrics.filter(
            participant__race__chart__program__date__gt=cutoff_date)
        race_key = get_race_key(venue_code, distance, grade_name)
        is_nominal = False
        training_arff = get_training_arff(
            race_key,
            training_metrics,
            is_nominal)
        testing_arff = get_testing_arff(
            race_key,
            testing_metrics,
            is_nominal)
        uuid_line_index = get_uuid_line_index(testing_arff)
        c = 0.01
        max_return = 0
        classifier_name = sys.argv[3]
        c_data = {
        "j48": {
        "c_start": 0.01,
        "c_stop": 0.49,
        "interval": 0.01,
        },
        "smo": {
        "c_start": 0,
        "c_stop": 6,
        "interval": 0.01,
        },
        }
        # prediction = sys.argv[7]

        c_start = c_data[classifier_name]["c_start"]
        c_stop = c_data[classifier_name]["c_stop"]
        interval = c_data[classifier_name]["interval"]


        jvm.start(packages=True, max_heap_size="5028m")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")


        print("\n\n{} Prediction Accuracy vs Confidence Factor".format(
            classifier_name.upper()))
        print("{} {} {}\n".format(venue_code, grade_name, distance))
        # print("Dogs Predicted to Finish {}".format(pred_format[prediction]))
        print(table_string.format(
            "C",
            "Win",
            "Place",
            "Show",
            "Bet Count",
            "Potential"))
        testing_data = build_scheduled_data(testing_arff)
        c = c_start
        while c <= c_stop:
            c = round(c, 2)
            print("C Factor: {}".format(c))
            # model_name = create_model(training_arff, classifier_name, str(c), race_key, loader)
            # model = Classifier(jobject=serialization.read(model_name))
            #
            # prediction_list = get_prediction_list(model, testing_data, uuid_line_index)
            # self.print_returns(prediction_list, str(c), race_key, loader, prediction)
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
