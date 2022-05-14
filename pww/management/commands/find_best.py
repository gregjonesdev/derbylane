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
from pww.utilities.weka import remove_uuid
from pww.utilities.testing import evaluate_model_cutoffs
from weka.classifiers import MultiSearch
import weka.core.packages as packages
from weka.classifiers import Classifier
from weka.core.classes import ListParameter, MathParameter

class Command(BaseCommand):

    def find_best_setup(self, train):
        loader = conv.Loader(classname=
            "weka.core.converters.ArffLoader")
        model_data = loader.load_file(train)
        model_data = remove_uuid(model_data)
        model_data.class_is_last()
        multi = MultiSearch(options=["-S", "1"])
        multi.evaluation = "CC"
        mparam = MathParameter()
        mparam.prop = "classifier.kernel.gamma"
        mparam.minimum = -3.0
        mparam.maximum = 3.0
        mparam.step = 1.0
        mparam.base = 10.0
        mparam.expression = "pow(BASE,I)"
        lparam = ListParameter()
        lparam.prop = "classifier.C"
        lparam.values = ["-2.0", "-1.0", "0.0", "1.0", "2.0"]
        multi.parameters = [mparam, lparam]
        cls = Classifier(
            classname="weka.classifiers.functions.SMOreg",
            options=["-K", "weka.classifiers.functions.supportVector.RBFKernel"])

        multi.classifier = cls
        multi.build_classifier(model_data)
        print("Model:\n" + str(multi))
        print("\nBest setup:\n" + multi.best.to_commandline())

    def get_training_metrics(self, venue_code, grade):

        return Metric.objects.filter(
            participant__race__grade__name=grade,
            participant__race__chart__program__venue__code=venue_code,
            participant__race__chart__program__date__range=(
                "2020-01-01",
                "2021-12-31"))

    def handle(self, *args, **options):
        classifier_name = "smoreg"
        venue_code = "TS"
        grade = "B"
        race_key = 'smoreg'
        training_metrics = self.get_training_metrics(venue_code, grade)
        training_arff = get_training_arff(
            race_key,
            training_metrics)
        jvm.start(
            packages=True,
            max_heap_size="5028m"
        )
        self.find_best_setup(training_arff)
        jvm.stop()
