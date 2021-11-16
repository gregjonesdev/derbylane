import datetime
import sys

from time import time
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from miner.utilities.urls import arff_directory
from miner.utilities.constants import focused_distances
from rawdat.models import Participant
from pww.models import TestPrediction, Metric
from pww.utilities.ultraweka import (
    create_model,
    build_scheduled_data,
    get_uuid_line_index,
    get_prediction_list)
from weka.classifiers import Classifier
import weka.core.converters as conv
import weka.core.jvm as jvm
import weka.core.serialization as serialization
from pww.utilities.arff import create_arff
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

    # def find_quinella_pairings(self, wheel, race, second_prediction):
    #     totals = []
    #     for participant in race.participant_set.all():
    #         if prediction_list[participant.uuid] = second_prediction and not participant = wheel:
    #             # add total
    #
    # def get_race_quinella_returns(self, prediction_list, race, first_prediction, second_prediction):
    #     quinella_returns = []
    #     second = None
    #     for participant in race.participant_set.all():
    #         if prediction_list[participant.uuid] = first_prediction:
    #             first.append(participant)
    #

    def get_same(self, prediction_list, race, prediction):
        matches_prediction = []
        for participant in race.participant_set.all():
            if prediction_list[participant.uuid] = prediction:
                matches_prediction.append(participant)
        i = 0
        unique_tuples = []
        while i < len(matches_prediction):
            j = i + 1
            while j < len(matches_prediction):
                unique_tuples.append((matches_prediction[i], matches_prediction[j]))
                j += 1
            i += 1
        print("unique tuples:")
        print(unique_tuples)


    def get_different(self, prediction_list, race, first_prediction, second_prediction):
        # matches_prediction = []
        # for participant in race.participant_set.all():
        #     if prediction_list[participant.uuid] = prediction:
        #         matches_prediction.append(participant)
        # i = 0
        # unique_tuples = []
        # while i < len(matches_prediction):
        #     j = i + 1
        #     while j < len(matches_prediction):
        #         unique_tuples.append((matches_prediction[i], matches_prediction[j]))
        #         j += 1
        #     i += 1
        # print("unique tuples:")
        # print(unique_tuples)




    def get_unique_quinellas(self, prediction_list, race, first_prediction, second_prediction):
        print("Testing:")
        predictions = [first_prediction, second_prediction]
        for participant in race.participant_set.all():
            print("{}: {}".format(participant.uuid, prediction_list[participant.uuid]))

        if first_prediction == second_prediction:
            self.get_same(race, first_prediction)

        else:
            self.get_different(race, first_prediction, second_prediction)


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
        i = 0
        matches_prediction = [1, 3, 5, 7]
        unique_tuples = []
        while i < len(matches_prediction):
            j = i + 1
            while j < len(matches_prediction):
                unique_tuples.append((matches_prediction[i], matches_prediction[j]))
                j += 1
            i += 1
        print("unique tuples:")
        print(unique_tuples)
        raise SystemExit(0)





        venue_code = "WD"
        grade_name = sys.argv[5]
        distance = focused_distances[venue_code][0]
        today = datetime.datetime.now()
        cutoff_date = (today - datetime.timedelta(days=49)).date()
        # training_cutoff = (today - datetime.timedelta(days=7)).date()
        start_time = time()
        all_metrics = Metric.objects.filter(
            participant__race__chart__program__venue__code=venue_code,
            participant__race__distance=distance,
            participant__race__grade__name=grade_name,
            participant__race__chart__program__date__gte="2019-01-01")
        training_metrics = all_metrics.filter(participant__race__chart__program__date__lte=cutoff_date)
        testing_metrics = all_metrics.filter(participant__race__chart__program__date__gt=cutoff_date)
        race_key = "{}_{}_{}".format(venue_code, distance, grade_name)


        training_arff_filename = "{}/train_{}.arff".format(
            arff_directory,
            race_key)
        testing_arff_filename = "{}/test_{}.arff".format(
            arff_directory,
            race_key)
        is_nominal = False
        # print("training metrics: {}".format(len(training_metrics)))
        training_arff = create_arff(
            training_arff_filename,
            training_metrics,
            is_nominal,
            True)
        testing_arff = create_arff(
            testing_arff_filename,
            testing_metrics,
            is_nominal,
            False)
        c = 0.01
        max_return = 0


        jvm.start(packages=True, max_heap_size="5028m")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")
        classifier_name = sys.argv[3]
        c_data = {
            "j48": {
                "c_start": 0.01,
                "c_stop": 0.49,
                "interval": 0.01,
            },
            "smo": {
                "c_start": 0,
                "c_stop": 2,
                "interval": 0.01,
            },
        }
        prediction = sys.argv[7]

        c_start = c_data[classifier_name]["c_start"]
        c_stop = c_data[classifier_name]["c_stop"]
        interval = c_data[classifier_name]["interval"]


        print("\n\n{} Prediction Accuracy vs Confidence Factor".format(
            classifier_name.upper()))
        print("{} {} {}\n".format(venue_code, grade_name, distance))
        print("Dogs Predicted to Finish {}".format(pred_format[prediction]))
        print(table_string.format(
            "C",
            "Win",
            "Place",
            "Show",
            "Bet Count",
            "Potential"))
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
