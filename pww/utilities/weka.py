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
    "weka.classifiers.rules.ZeroR",
    "weka.classifiers.functions.SMOreg",
    "weka.classifiers.trees.REPTree",
    "weka.clusterers.SimpleKMeans",
    ]

def output_predictions(cls, data):
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

def train_classifier(data, classifier, options):
    data.class_is_last()
    cls = Classifier(classname=classifier, options=options)
    cls.build_classifier(data)
    return cls


def make_predictions(scheduled_csv, results_csv):
    print("make predcitions")
    jvm.start(packages=True, system_info=True, max_heap_size="512m")
    # loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    # data=loader.load_file(results_csv)
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    # data=loader.load_file(data_dir + "weather.numeric.arff")
    data=loader.load_file(results_csv)

    cls = train_classifier(data, "weka.classifiers.trees.J48", ["-C", "0.3"])
    output_predictions(cls, data)

    jvm.stop()
