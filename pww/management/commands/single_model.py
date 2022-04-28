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
from pww.utilities.ultraweka import create_model
from pww.utilities.testing import evaluate_model_cutoffs

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--venue', type=str)
        parser.add_argument('--grade', type=str)
        parser.add_argument('--prediction', type=str)

    def handle(self, *args, **options):
        c_factor = 0.5
        classifier_name = "j48"
        race_key = "universal"
        venue_code = sys.argv[3]
        grade = sys.argv[5]
        target_prediction = sys.argv[7]
        training_metrics = Metric.objects.filter(
            participant__race__grade__name=grade,
            # participant__race__distance=550,
            participant__race__chart__program__venue__code=venue_code,
            participant__race__chart__program__date__range=(
                "2019-06-01",
                "2021-12-31"))
        is_nominal = False
        training_arff = get_training_arff(
            race_key,
            training_metrics,
            is_nominal)
        jvm.start(
            packages=True,
            max_heap_size="5028m"
        )
        loader = conv.Loader(classname=
            "weka.core.converters.ArffLoader")
        model = create_model(
            training_arff,
            classifier_name,
            str(c_factor),
            race_key,
            loader)
        print("\nAvg Returns for dogs predicted to finish: {}".format(
            target_prediction))
        print("Training Metrics: {}\n".format(
            len(training_metrics)))

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
        evaluate_model_cutoffs(
            model,
            target_prediction,
            testing_arff)
        jvm.stop()
