import os

from django.core.management.base import BaseCommand

import weka.core.jvm as jvm
import weka.core.converters as conv

from weka.classifiers import Evaluation, Classifier
from weka.core.classes import Random

confidence_vector = "0.3"
data_dir = "./rawdat/arff/"

classifiers = [
    "weka.classifiers.functions.SMO",
    "weka.classifiers.trees.J48",
    ]

class Command(BaseCommand):

    def build_attributes():
        attributes = []
        attributes.append(
            Attribute.create_numeric("scaled_fastest_time"))
        attributes.append(Attribute.create_nominal("sex", ["M", "F"]))
        return attributes

    def create_dataset(dataset_name):
        return Instances.create_instances(
            dataset_name,
            self.build_attributes(),
            0)

    def populate_dataset(dataset):
        for metric in metrics:
            inst = Instance.create_instance(metric)
            dataset.add_instance(inst)
        return dataset

    # def build_classifier(self, data, classname, options):


    #
    # def experiment():
    #     datasets = ["iris.arff", "anneal.arff"]
    #     classifiers = [Classifier(classname="weka.classifiers.rules.ZeroR"), Classifier(classname="weka.classifiers.trees.J48")]
    #     outfile = "results-cv.arff"   # store results for later analysis
    #     exp = SimpleCrossValidationExperiment(
    #         classification=True,
    #         runs=10,
    #         folds=10,
    #         datasets=datasets,
    #         classifiers=classifiers,
    #         result=outfile)
    #     exp.setup()
    #     exp.run()
    #     # evaluate previous run
    #     loader = converters.loader_for_file(outfile)
    #     data   = loader.load_file(outfile)
    #     matrix = ResultMatrix(classname="weka.experiment.ResultMatrixPlainText")
    #     tester = Tester(classname="weka.experiment.PairedCorrectedTTester")
    #     tester.resultmatrix = matrix
    #     comparison_col = data.attribute_by_name("Percent_correct").index
    #     tester.instances = data
    #     print(tester.header(comparison_col))
    #     print(tester.multi_resultset_full(0, comparison_col))

    def train_classifier(self, data, classifier, options):
        data.class_is_last()
        cls = Classifier(classname=classifier, options=options)
        cls.build_classifier(data)
        return cls

    def output_predictions(self, cls, data):
        data.class_is_last()
        for index, inst in enumerate(data):
            print("{} | {}".format(index, inst))
            pred = cls.classify_instance(inst)
            # print(pred)
            dist = cls.distribution_for_instance(inst)
            print(
            str(index+1) +
            ": label index=" +
            str(pred) +
            ", class distribution=" +
            str(dist))



    def handle(self, *args, **options):
        self.stdout.write("Starting Weka script..\n")
        jvm.start(packages=True, system_info=True, max_heap_size="512m")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")
        data=loader.load_file(data_dir + "weather.numeric.arff")
        cls = self.train_classifier(data, "weka.classifiers.trees.J48", ["-C", "0.3"])
        self.output_predictions(cls, data)

        jvm.stop()
