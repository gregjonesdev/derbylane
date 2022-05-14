import sys
import weka.core.converters as conv
import weka.core.jvm as jvm

from django.core.management.base import BaseCommand
from pww.models import Metric
from miner.utilities.constants import focused_grades
from pww.utilities.arff import (
    get_training_arff,
    get_testing_arff,
)
from pww.utilities.classifiers import classifiers
from pww.utilities.ultraweka import get_classifier
from pww.utilities.weka import create_model
from pww.utilities.testing import evaluate_model_cutoffs, evaluate_nominal_model

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str)
        parser.add_argument('--venue', type=str)
        parser.add_argument('--grade', type=str)
        parser.add_argument('--prediction', type=str)

    def handle(self, *args, **options):
        classifier_name = sys.argv[3]
        venue_code = sys.argv[5]
        grade = sys.argv[7]
        # target_prediction = sys.argv[9]
        training_metrics = Metric.objects.filter(
            participant__race__grade__name=grade,
            # participant__race__distance=550,
            participant__race__chart__program__venue__code=venue_code,
            participant__race__chart__program__date__range=(
                "2020-01-01",
                "2021-12-31"))
        classifier_attributes = classifiers[classifier_name]
        training_arff = get_training_arff(
            classifier_name,
            training_metrics,
            classifier_attributes["is_nominal"])
        jvm.start(
            packages=True,
            max_heap_size="5028m"
        )
        print("47")
        # classifier = get_classifier(
        #     training_arff,
        #     classifier_attributes)
        from weka.core.converters import Loader
        loader = Loader(classname="weka.core.converters.ArffLoader")
        create_model(training_arff, classifier_name, "0.5", "race_key", loader)



        print("48")
        # print("\nAvg Returns for dogs predicted to finish: {}".format(
        #     target_prediction))
        print("Training Metrics: {}\n".format(
            len(training_metrics)))
        raise SystemExit(0)
        testing_metrics = Metric.objects.filter(
            participant__race__chart__program__venue__code=venue_code,
            participant__race__grade__name=grade,
            participant__race__chart__program__date__range=(
                "2022-01-01",
                "2022-04-20"))
        testing_arff = get_testing_arff(
            "{}_{}".format(venue_code, grade),
            testing_metrics,
            is_nominal)
        print("Testing Metrics: {}".format(len(testing_metrics)))


        evaluate_nominal_model(
            model,
            # target_prediction,
            testing_arff)
        jvm.stop()
