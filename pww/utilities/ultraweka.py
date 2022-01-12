from weka.filters import Filter
import weka.core.jvm as jvm
import weka.core.packages as packages
import weka.core.converters as conv
import weka.core.serialization as serialization
from libsvm.svmutil import *
from rawdat.models import Participant
from weka.classifiers import Classifier, Evaluation
from django.core.exceptions import ObjectDoesNotExist
from pww.models import Prediction, Metric
from weka.attribute_selection import ASSearch
from weka.attribute_selection import ASEvaluation
# from weka.attribute_selection import AttributeSelection
from weka.core.classes import Random
from weka.core.converters import Loader
from weka.core.dataset import Instances
from weka.filters import Filter

from weka.core.packages import install_missing_packages, LATEST
from miner.utilities.constants import csv_columns
import os
import pprint


classifiers = {
    "smo": {
        "classname": "weka.classifiers.functions.SMO",
        "options": [
            "-L", "0.001",
            "-P", "1.0E-12",
            "-N", "0",
            "-W", "1",
            "-V", "10",
            "-K", "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007",
            "-calibrator", "weka.classifiers.functions.Logistic -R 1.0E-8 -M -1 -num-decimal-places 4"
        ],
    },
    "j48": {
        "classname": "weka.classifiers.trees.J48",
        "options": [],
    },
    "randomforest": {
        "classname": "weka.classifiers.trees.RandomForest",
        "options": [
            #  "-B", # Break ties randomly when several attributes look equally good.
            # "-U" # Allow unclassified instances.
        ],
    },
    "nbu": {
        "classname": "weka.classifiers.bayes.NaiveBayesUpdateable",
        "options": [],
    },
    "nb": {
        "classname": "weka.classifiers.bayes.NaiveBayes",
        "options": [],
    },
    "zeror": {
        "classname": "weka.classifiers.rules.ZeroR",
        "options": [],
    },
    "reptree": {
        "classname": "weka.classifiers.trees.REPTree",
        "options": [],
    },
    # "simplek": {
    #     "classname": "weka.clusterers.SimpleKMeans",
    #     "options": [],
    # },
    "ll": {
        "classname": "weka.classifiers.functions.LibLINEAR",
        "options": [],
    },
    "smoreg": {
        "classname": "weka.classifiers.functions.SMOreg",
        "options": [],
    },
}


def get_metrics(venue_code, distance, grade_name):
    return Metric.objects.filter(
        participant__race__chart__program__venue__code=venue_code,
        participant__race__distance=distance,
        participant__race__grade__name=grade_name,
        participant__race__chart__program__date__gte="2019-01-01")

def add_c_to_options(options, c):
    # print(options)
    if "-C" in options:
        c_index = options.index("-C") + 1
        options[c_index] = c
    else:
        options.append("-C")
        options.append(c)
    # print(options)
    return options

def create_model(training_arff, classifier_name, c, race_key, loader):
    classifier = classifiers[classifier_name]
    options = classifier["options"]
    # options.append("-C")
    # options.append(str(c))
    # print(options)
    if c:
        options = add_c_to_options(options, c)

    classname = classifier["classname"]
    model_data = loader.load_file(training_arff)
    model_data = remove_uuid(model_data)
    model_data = nominalize(model_data)
    model_data.class_is_last()
    classifier = Classifier(classname="weka.classifiers.meta.AttributeSelectedClassifier")
    search = ASSearch(classname="weka.attributeSelection.BestFirst", options=["-D", "1", "-N", "3"])
    evaluator = ASEvaluation(classname="weka.attributeSelection.CfsSubsetEval", options=["-P", "1", "-E", "1"])
    base = Classifier(classname=classname, options=options)

    classifier.set_property("classifier", base.jobject)
    classifier.set_property("evaluator", evaluator.jobject)
    classifier.set_property("search", search.jobject)

    classifier.build_classifier(model_data)

    filename = "test_models/{}_{}_{}.model".format(
        race_key,
        classifier_name,
        c.replace(".", "")
    )
    serialization.write(filename, classifier)
    return Classifier(jobject=serialization.read(filename))
     # -U
     #  Use unpruned tree.
     #
     # -O
     #  Do not collapse tree.
     #
     # -C <pruning confidence>
     #  Set confidence threshold for pruning.
     #  (default 0.25)
     #
     # -M <minimum number of instances>
     #  Set minimum number of instances per leaf.
     #  (default 2)
     #
     # -R
     #  Use reduced error pruning.
     #
     # -N <number of folds>
     #  Set number of folds for reduced error
     #  pruning. One fold is used as pruning set.
     #  (default 3)
     #
     # -B
     #  Use binary splits only.
     #
     # -S
     #  Don't perform subtree raising.
     #
     # -L
     #  Do not clean up after the tree has been built.
     #
     # -A
     #  Laplace smoothing for predicted probabilities.
     #
     # -J
     #  Do not use MDL correction for info gain on numeric attributes.
     #
     # -Q <seed>
     #  Seed for random data shuffling (default 1).
     #
     # -doNotMakeSplitPointActualValue
     #  Do not make split point actual value.
     #


def remove_uuid(data):
    remove = Filter(
        classname="weka.filters.unsupervised.attribute.Remove",
        options=["-R", "first"])
    remove.inputformat(data)
    return remove.filter(data)


def nominalize(data):
    nominalize = Filter(
        classname="weka.filters.unsupervised.attribute.NumericToNominal",
        options=["-R", "{}".format(csv_columns.index('Fi'))])
    nominalize.inputformat(data)
    return nominalize.filter(data)


def get_uuid_line_index(filename):
    arff_file = open(filename, "r")
    uuid_line_index = {}
    i = 0
    for line in arff_file:
        if len(line) > 100:
            split_line = line.split(",")
            uuid = line.split(",")[0]
            uuid_line_index[i] = uuid
            i += 1
    return uuid_line_index

def get_prediction_list(testing_arff, model, confidence_cutoff):
    uuid_line_index = get_uuid_line_index(testing_arff)
    testing_data = build_scheduled_data(testing_arff)
    prediction_list = {}

    for index, inst in enumerate(testing_data):
        if index in uuid_line_index.keys():
            uuid = uuid_line_index[index]
            prediction = model.classify_instance(inst)
            dist = model.distribution_for_instance(inst)
            print(dist)
            participant = Participant.objects.get(uuid=uuid)
            index = int(model.classify_instance(inst))
            confidence = dist[index]
            if confidence >= confidence_cutoff:
                prediction_list[uuid] = prediction
                print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                    participant.race.chart.program.date,
                    participant.race.chart.program.venue.code,
                    participant.race.number,
                    "{}-{}".format(
                        participant.post,
                        participant.dog.name[:5]),
                    model.classify_instance(inst),
                    round(confidence, 2),
                    round(dist[0], 2),
                    round(sum(dist[:2]), 2),
                    round(sum(dist[:3]), 2)))
    return prediction_list

def get_prediction(participant):
    try:
        pred = Prediction.objects.get(participant=participant)
    except ObjectDoesNotExist:
        new_pred = Prediction(
            participant = participant
        )
        new_pred.set_fields_to_base()
        new_pred.save()
        pred = new_pred
    return pred

def build_scheduled_data(arff_data):
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    loaded_data = loader.load_file(arff_data)
    anonymous_data = remove_uuid(loaded_data)
    scheduled_data = nominalize(anonymous_data)
    scheduled_data.class_is_last()
    return scheduled_data



def get_prediction_confidence(testing_arff, model, target_prediction, confidence_cutoff):
    uuid_line_index = get_uuid_line_index(testing_arff)
    testing_data = build_scheduled_data(testing_arff)
    prediction_confidence = {}
    for index, inst in enumerate(testing_data):

        if index in uuid_line_index.keys():
            uuid = uuid_line_index[index]
            # print(uuid)
            prediction = model.classify_instance(inst)
            # print(prediction)
            # print(target_prediction)
            # print(int(prediction) == int(target_prediction))
            dist = model.distribution_for_instance(inst)
            index = int(prediction) # SMO only 0-7
            confidence = dist[index]
            # print(dist)
            if int(prediction) == int(target_prediction):
                if confidence >= confidence_cutoff:
                    prediction_confidence[uuid] = (prediction, confidence)

    return prediction_confidence
