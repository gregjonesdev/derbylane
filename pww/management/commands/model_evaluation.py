import sys
from weka.core.converters import Loader

import weka.core.jvm as jvm

from django.core.management.base import BaseCommand
from pww.models import Metric
from miner.utilities.constants import focused_grades
from pww.utilities.arff import (
    get_training_arff,
    get_testing_arff,
)
from pww.utilities.classifiers import classifiers
from pww.utilities.weka import get_model, evaluate_predictions
from pww.utilities.weka import create_model
from pww.utilities.testing import evaluate_model_cutoffs, evaluate_nominal_model
from pww.utilities.metrics import get_training_metrics

betting_distances = {
    "WD": 548,
    "TS": 550,
    "SL": 583
}

model_directory = "test_models"

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str)
        parser.add_argument('--venue', type=str)
        parser.add_argument('--grade', type=str)
        parser.add_argument('--start', type=str)

    def handle(self, *args, **options):
        classifier_name = sys.argv[3]
        venue_code = sys.argv[5]
        grade_name = sys.argv[7]
        start_date = sys.argv[9]
        end_date = "2021-12-31"
        test_start = "2022-01-01"
        test_stop = "2022-04-20"
        training_metrics = get_training_metrics(
            grade_name,
            venue_code,
            start_date,
            end_date)
        training_arff = get_training_arff(
            classifier_name,
            training_metrics)
        jvm.start(
            packages=True,
            max_heap_size="5028m"
        )


        print("{} Grade {}".format (venue_code, grade_name))
        print("{} - {}".format(start_date, end_date))
        print("Training Metrics: {}\n".format(
            len(training_metrics)))

        testing_metrics = get_training_metrics(
            grade_name,
            venue_code,
            test_start,
            test_stop)
        testing_arff = get_testing_arff(
            "{}_{}".format(venue_code, grade_name),
            testing_metrics)
        print("Testing Metrics: {}".format(len(testing_metrics)))

        # Must build test model
        model = get_model(venue_code, grade_name, start_date, model_directory)

        evaluate_predictions(
            testing_arff,
            model,
            classifier_name)
        jvm.stop()
