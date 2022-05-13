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
from pwww.utilities.weka import remove_uuid
from pww.utilities.testing import evaluate_model_cutoffs
from weka.classifiers import MultiSearch
import weka.core.packages as packages
from weka.classifiers import Classifier
from weka.core.classes import ListParameter, MathParameter

class Command(BaseCommand):

    def create_model(self, train):
        loader = conv.Loader(classname=
            "weka.core.converters.ArffLoader")
        model_data = loader.load_file(train)
        model_data = remove_uuid(model_data)
        model_data.class_is_last()
        # multi = MultiSearch(
        # options=["-sample-size", "100.0", "-initial-folds", "2", "-subsequent-folds", "2",
        #          "-num-slots", "1", "-S", "1"])
        multi = MultiSearch(options=["-S", "1"])

        # javabridge.jutil.JavaException: Illegal options:
        # -sample-size 100.0
        # -initial-folds 2
        # -subsequent-folds 2
        # -num-slots 1

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

#         File "/home/greg/derbylane/dl_env/lib/python3.8/site-packages/weka/classifiers.py", line 104, in build_classifier
#     self._header = data.copy_structure()
# AttributeError: 'str' object has no attribute 'copy_structure'
        print("51")
        multi.classifier = cls
        multi.build_classifier(model_data)
        print("Model:\n" + str(multi))
        print("\nBest setup:\n" + multi.best.to_commandline())

    def handle(self, *args, **options):
        print("handle")
        print(packages.__dict__)
        test_arff = "arff/numerictest2.arff"
        classifier_name = "smoreg"
        jvm.start(
            packages=True,
            max_heap_size="5028m"
        )
        self.create_model(test_arff)
        jvm.stop()
