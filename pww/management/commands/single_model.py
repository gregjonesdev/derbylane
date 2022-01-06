import weka.core.converters as conv
import weka.core.jvm as jvm

from django.core.management.base import BaseCommand
from pww.models import Metric
from miner.utilities.constants import focused_grades
from pww.utilities.arff import (
    get_training_arff,
    get_testing_arff,
)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--grade', type=str)
        parser.add_argument('--prediction', type=str)

    def handle(self, *args, **options):
        c_factor = 0.4
        cutoff = 0.85
        model_name = "j48"
        race_key = "universal"
        venue_codes = ["TS", "WD", "SL"]
        training_metrics = Metric.objects.filter(
            participant__race__chart__program__venue__code="TS",
            participant__race__chart__program__date__range=(
                "2018-01-01",
                "2021-11-04"))
        print("\nTraining Metrics: {}".format(
            len(training_metrics)))
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

        for venue_code in venue_codes:
            print("Venue: {}".format(venue_code))
            for grade in focused_grades[venue_code]:
                print("Grade: {}".format(grade))


        jvm.stop()
