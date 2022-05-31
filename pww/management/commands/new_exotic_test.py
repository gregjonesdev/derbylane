import csv
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
from pww.utilities.weka import get_model, save_model, evaluate_exotics
from pww.utilities.weka import create_model
from pww.utilities.testing import evaluate_model_cutoffs, evaluate_nominal_model
from pww.utilities.metrics import new_get_metrics, get_race_metrics


from rawdat.models import Race

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
        f = open('test_data.csv'.format(venue_code, grade_name), 'w')
        writer = csv.writer(f)
        end_date = "2021-12-31"
        test_start = "2022-01-01"
        test_stop = "2022-04-20"
        # test_start = "2022-05-16"
        # test_stop = "2022-05-19"

        print("{} Grade {} Exotic Analysis".format(venue_code, grade_name))
        print("{} - {}".format(test_start, test_stop))

        participants = []
        test_races = Race.objects.filter(
            chart__program__date__range=(test_start, test_stop),
            grade__name=grade_name,
            chart__program__venue__code=venue_code)

        print("{} Races Tested".format(test_races.count()))
        for race in test_races:
            for participant in race.participant_set.all():
                participants.append(participant)

        training_metrics = new_get_metrics(
            grade_name,
            venue_code,
            start_date,
            end_date)
        testing_metrics = []
        for race in test_races:
            metrics = get_race_metrics(race)
            for metric in metrics:
                testing_metrics.append(metric)
        print("Testing Metrics: {}".format(len(testing_metrics)))
        training_arff = get_training_arff(
            classifier_name,
            training_metrics)
        testing_arff = get_testing_arff(
            "{}_{}".format(venue_code, grade_name),
            testing_metrics)
        jvm.start(
            packages=True,
            max_heap_size="5028m"
        )
        print("{} Grade {}".format (venue_code, grade_name))
        print("{} - {}".format(start_date, end_date))
        print("Training Metrics: {}\n".format(
            len(training_metrics)))
        save_model(training_arff, classifier_name, model_directory, "exotic_test")
        model = get_model(model_directory, "exotic_test")

        # Must build test model
        evaluate_exotics(
            testing_arff,
            model,
            classifier_name,
            test_races,
            writer)
        jvm.stop()
        f.close()
