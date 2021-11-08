import datetime
import sys

from django.core.management.base import BaseCommand

from pww.models import TestPrediction, Metric

from miner.utilities.urls import arff_directory

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--venue', type=str)
        parser.add_argument('--grade', type=str)


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

    def handle(self, *args, **options):
        venue_code = "WD"
        grade_name = "A"
        distance = 548
        today = datetime.datetime.now()
        cutoff_date = (today - datetime.timedelta(weeks=26)).date()


        all_metrics = self.get_metrics(venue_code, distance, grade_name)
        training_metrics = all_metrics.filter(participant__race__chart__program__date__lte=cutoff_date)
        test_metrics = all_metrics.filter(participant__race__chart__program__date__gt=cutoff_date)
        print("All metrics: {}".format(len(all_metrics)))
        print("Training metrics: {}".format(len(training_metrics)))
        print("Test metrics: {}".format(len(test_metrics)))
