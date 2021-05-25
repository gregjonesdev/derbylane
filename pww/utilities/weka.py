import os

from django.core.management.base import BaseCommand
from weka.filters import Filter
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


# EXCLUDE Attribute without removing:
#  You can use the FilteredClassifier in conjunction with the Remove filter (weka.filters.unsupervised.attribute.Remove).
# remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1,2,3,4,5"])




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
    remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "first"])
    remove.inputformat(data)     # let the filter know about the type of data to filter
    filtered = remove.filter(data)   # filter the data
    print(filtered)                  #
    raise SystemExit(0)
    cls = train_classifier(data, "weka.classifiers.trees.J48", ["-C", "0.3"])
    output_predictions(cls, data)

    jvm.stop()
