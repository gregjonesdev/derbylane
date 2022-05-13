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
from pww.utilities.testing import evaluate_model_cutoffs
import weka.classifiers.MultiSearch as MultiSearch
import weka.core.packages as packages

from weka.core.classes import ListParameter, MathParameter

class Command(BaseCommand):

    def create_model(self, train):
        multi = MultiSearch(
        options=["-sample-size", "100.0", "-initial-folds", "2", "-subsequent-folds", "2",
                 "-num-slots", "1", "-S", "1"])
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
        multi.build_classifier(train)
        print("Model:\n" + str(multi))
        print("\nBest setup:\n" + multi.best.to_commandline())

    def handle(self, *args, **options):
        print("handle")
        print(MultiSearch.__dict__)
        test_arff = "arff/numerictest.arff"
        classifier_name = "smoreg"
        jvm.start(
            packages=True,
            max_heap_size="5028m"
        )
        packages.install_package("multisearch")
        items = packages.all_packages()
        for item in items:
            print(item.name)
        self.create_model(test_arff)
        jvm.stop()
