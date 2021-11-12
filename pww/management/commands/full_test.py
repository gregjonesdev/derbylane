import datetime
import sys

from time import time
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from miner.utilities.urls import arff_directory
from miner.utilities.constants import csv_columns
from rawdat.models import Participant
from pww.models import TestPrediction, Metric
from pww.utilities.ultraweka import (
    create_model,
    create_model,
    build_scheduled_data,
    get_uuid_line_index,
    get_prediction_list)
from weka.classifiers import Classifier
import weka.core.converters as conv
import weka.core.jvm as jvm
import weka.core.serialization as serialization
table_string = "{}\t\t{}\t\t{}\t\t{}\t\t{}"

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
    "1": "1st",
    "2": "2nd",
    "3": "3rd",
    "4": "4th"
}


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str)
        parser.add_argument('--prediction', type=str)
        # parser.add_argument('--grade', type=str)


    def create_arff(self, filename, metrics, is_nominal, cutoff_date):

        arff_file = open(filename, "w")
        arff_file.write("@relation Metric\n")
        arff_file = self.write_headers(arff_file, is_nominal)
        for metric in metrics:
            csv_metric = metric.build_csv_metric(cutoff_date)
            if csv_metric:
                arff_file.writelines(csv_metric)

        return filename

    def write_headers(self, arff_file, is_nominal):
        for each in csv_columns:
            if is_nominal and each == "Fi":
                arff_file.write("@attribute {} nominal\n".format(each))
            elif each == "PID":
                arff_file.write("@attribute PID string\n")
            elif each == "Se":
                arff_file.write("@attribute Se {M, F}\n")
            else:
                arff_file.write("@attribute {} numeric\n".format(each))
        arff_file.write("@data\n")
        return arff_file


    def get_metrics(self, venue_code, distance, grade_name):
        return Metric.objects.filter(
            participant__race__chart__program__venue__code=venue_code,
            participant__race__distance=distance,
            participant__race__grade__name=grade_name)




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


    def print_returns(self, model_name, testing_arff, c, race_key, loader, prediction):
        # print(model_name)
        model = Classifier(jobject=serialization.read(model_name))
        # print(type(testing_arff))
        uuid_line_index = get_uuid_line_index(testing_arff)
        # print(uuid_line_index)
        testing_data = build_scheduled_data(testing_arff)
        # model.build_classifier(testing_data)
        print(testing_data)
        print(uuid_line_index)
        prediction_list = get_prediction_list(model, testing_data, uuid_line_index)

        win_returns = 0
        place_returns = 0
        show_returns = 0
        bet_count = 0
        # Only focus on prediction = 4!
        guesses = {}
        # for uuid in prediction_list:
        #     guess = str(int(prediction_list[uuid]))
        #     if not guess in guesses.keys():
        #         guesses[guess] = 1
        #     else:
        #         guesses[guess] += 1
        # print(guesses)




            # if int(prediction_list[uuid]) == int(prediction):
            #     bet_count += 1
            #     participant = Participant.objects.get(uuid=uuid)
            #     win_returns += self.get_win_return(participant)
            #     place_returns += self.get_place_return(participant)
            #     show_returns += self.get_show_return(participant)

        # for uuid in prediction_list:
        #     self.save_prediction(uuid, int(prediction_list[uuid]), c)
        # average_returns = self.get_average_returns(c, )
        # create_model(arff_file, options, root_filename)
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
                bet_count))




    def handle(self, *args, **options):
        venue_code = "WD"
        grade_name = "A"
        distance = 548
        today = datetime.datetime.now()
        cutoff_date = (today - datetime.timedelta(weeks=26)).date()
        training_cutoff = (today - datetime.timedelta(days=2)).date()
        start_time = time()
        all_metrics = self.get_metrics(venue_code, distance, grade_name)
        training_metrics = all_metrics.filter(participant__race__chart__program__date__lte=cutoff_date)
        testing_metrics = all_metrics.filter(participant__race__chart__program__date__range=[cutoff_date, training_cutoff])

        race_key = "{}_{}_{}".format(venue_code, distance, grade_name)


        training_arff_filename = "{}/train_{}.arff".format(
            arff_directory,
            race_key)
        testing_arff_filename = "{}/test_{}.arff".format(
            arff_directory,
            race_key)
        is_nominal = False

        training_arff = self.create_arff(
            training_arff_filename,
            training_metrics,
            is_nominal,
            cutoff_date)
        testing_arff = self.create_arff(
            testing_arff_filename,
            testing_metrics,
            is_nominal,
            cutoff_date)
        c = 0.01
        max_return = 0
        jvm.start(packages=True, max_heap_size="5028m")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")
        classifier_name = sys.argv[3]
        prediction = sys.argv[5]
        print("\n\n{} Prediction Accuracy vs Confidence Factor".format(
            classifier_name.upper()))
        print("{} {} {}\n".format(venue_code, grade_name, distance))
        print("Dogs Predicted to Finish {}".format(pred_format[prediction]))
        print(table_string.format(
            "C",
            "Win",
            "Place",
            "Show",
            "Bet Count"))
        while c <= 0.3:


            c = round(c, 2)
            model_name = create_model(training_arff, classifier_name, str(c), race_key, loader)
            self.print_returns(model_name, testing_arff, str(c), race_key, loader, prediction)
            c = round(c + 0.01, 2)

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
