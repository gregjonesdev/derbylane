import datetime
import sys
from time import time

from django.core.management.base import BaseCommand

from pww.models import TestPrediction, Metric

from miner.utilities.urls import arff_directory
from miner.utilities.constants import csv_columns

from weka.filters import Filter
import weka.core.jvm as jvm
import weka.core.packages as packages
import weka.core.converters as conv
import weka.core.serialization as serialization
from libsvm.svmutil import *
from rawdat.models import Participant
from weka.classifiers import Classifier, Evaluation
from django.core.exceptions import ObjectDoesNotExist
from pww.models import Prediction
from weka.attribute_selection import ASSearch
from weka.attribute_selection import ASEvaluation
from weka.attribute_selection import AttributeSelection
# import wekaexamples.helper as helper
from weka.core.classes import Random
from weka.core.converters import Loader
from weka.core.dataset import Instances
from weka.filters import Filter

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


    def get_options(self, c):

        # jason_comment = '''
        # weka.classifiers.functions.SMO -C 1.25 -L 0.001 -P 1.0E-12 -N 0 -V -1 -W 1 -K
        # "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007"
        # -calibrator "weka.classifiers.functions.Logistic -R 1.0E-8 -M -1 -num-decimal-places 4"
        # '''

        return [
        "-C", c, # The complexity constant C. (default 1)
        "-L", "0.001",
        "-P", "1.0E-12", # The epsilon for round-off error. (default 1.0e-12)
        "-N", "0", # Whether to 0=normalize/1=standardize/2=neither. (default 0=normalize)
        "-W", "1", # The random number seed. (default 1)
        "-V", "10", # The number of folds for the internal cross-validation. (default -1, use training data)
        # Following line will be included in Kernel instantiation
        "-K", "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007",
        "-calibrator", "weka.classifiers.functions.Logistic -R 1.0E-8 -M -1 -num-decimal-places 4"
        ]

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

    def create_model(training_arff, c, race_key):

        # model_name = SL_583_D_smo_075.model

        # jvm.start(packages=True, max_heap_size="5028m")
        #
        # loader = conv.Loader(classname="weka.core.converters.ArffLoader")
        model_data = loader.load_file(training_arff)
        model_data = remove_uuid(model_data)
        model_data = nominalize(model_data)
        model_data.class_is_last()
        classifier = Classifier(classname="weka.classifiers.meta.AttributeSelectedClassifier")
        search = ASSearch(classname="weka.attributeSelection.BestFirst", options=["-D", "1", "-N", "3"])
        evaluator = ASEvaluation(classname="weka.attributeSelection.CfsSubsetEval", options=["-P", "1", "-E", "1"])
        base = Classifier(classname="weka.classifiers.functions.SMO", options=options)

        classifier.set_property("classifier", base.jobject)
        classifier.set_property("evaluator", evaluator.jobject)
        classifier.set_property("search", search.jobject)

        classifier.build_classifier(model_data)
        filename = "test_models/{}.model".format(filename)
        serialization.write(filename, classifier)
        jvm.stop()
        print("Model Created Successfully.")
        print("Filename: {}".format(filename))

    def print_returns(self, training_arff, c):

        # model = self.create_model(training_arff, c, race_key)
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
        test_metrics = all_metrics.filter(participant__race__chart__program__date__gt=cutoff_date)

        race_key = "{}_{}_{}".format(venue_code, distance, grade_name)

        print("SMO Prediction Accuracy vs Confidence Factor")
        print("{} {} {}\n".format(venue_code, grade_name, distance))

        arff_filename = "{}/{}.arff".format(
            arff_directory,
            race_key)
        is_nominal = False

        training_arff = self.create_arff(
            arff_filename,
            training_metrics,
            is_nominal,
            cutoff_date)
        c = 0.1
        max_return = 0
        jvm.start(packages=True, max_heap_size="5028m")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")

        while c <= 10:
            c = round(c, 2)
            self.print_returns(training_arff, c)
            c = round(c + 0.1, 2)

        end_time = time()

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
