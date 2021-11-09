import datetime
import sys

from time import time
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from miner.utilities.urls import arff_directory
from miner.utilities.constants import csv_columns
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
table_string = "{}\t\t{}\t\t{}\t\t{}"

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

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--venue', type=str)
        parser.add_argument('--grade', type=str)

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
        if value >= max:
            formatting += bcolors.BOLD
        return formatting + "${}".format(round(value, 2)) + bcolors.ENDC


    def save_prediction(self, participant_uuid, smo_prediction, c):
        pass
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


    def print_returns(self, model_name, testing_arff, c, race_key, loader):
        print("print returns")
        # print(model_name)
        model = Classifier(jobject=serialization.read(model_name))
        # print(type(testing_arff))
        uuid_line_index = get_uuid_line_index(testing_arff)
        # print(uuid_line_index)
        testing_data = build_scheduled_data(testing_arff)
        # model.build_classifier(testing_data)
        prediction_list = get_prediction_list(model, testing_data, uuid_line_index)
        print(prediction_list)
        print(c)
        print(type(c))
        for uuid in prediction_list:
            self.save_prediction(uuid, int(prediction_list[uuid]), c)
        raise SystemExit(0)
        # average_returns = self.get_average_returns(c, )
        # create_model(arff_file, options, root_filename)
        average_returns = [2.1, 2.0, 0.5]
        max_return = max(average_returns)
        print(table_string.format(
            c,
            self.get_formatting(max_return, average_returns[0]),
            self.get_formatting(max_return, average_returns[1]),
            self.get_formatting(max_return, average_returns[2])))




    def handle(self, *args, **options):
        venue_code = "WD"
        grade_name = "A"
        distance = 548
        today = datetime.datetime.now()
        cutoff_date = (today - datetime.timedelta(weeks=26)).date()
        start_time = time()

        all_metrics = self.get_metrics(venue_code, distance, grade_name)
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
        c = 0.1
        max_return = 0
        jvm.start(packages=True, max_heap_size="5028m")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")

        print("\n\nSMO Prediction Accuracy vs Confidence Factor")
        print("{} {} {}\n".format(venue_code, grade_name, distance))
        while c <= 10:
            c = round(c, 2)
            model_name = create_model(training_arff, str(c), race_key, loader)
            self.print_returns(model_name, testing_arff, str(c), race_key, loader)
            c = round(c + 0.1, 2)

        jvm.stop()
        end_time = time()
        seconds_elapsed = end_time - start_time

        hours, rest = divmod(seconds_elapsed, 3600)
        minutes, seconds = divmod(rest, 60)

        print("\nAll metrics: {}".format(len(all_metrics)))
        print("Training metrics: {}".format(len(training_metrics)))
        print("Test metrics: {}".format(len(test_metrics)))

        print("\nCompleted Analysis in {}:{}:{}".format(
        self.two_digitizer(int(hours)),
        self.two_digitizer(int(minutes)),
        self.two_digitizer(int(seconds))))
