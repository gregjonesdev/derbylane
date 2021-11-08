from weka.filters import Filter
import weka.core.jvm as jvm
import weka.core.packages as packages
import weka.core.converters as conv
import weka.core.serialization as serialization
from libsvm.svmutil import *
from rawdat.models import Participant
from weka.classifiers import Classifier, Evaluation
from django.core.exceptions import ObjectDoesNotExist
from pww.models import Prediction
from weka.attribute_selection import ASSearch
from weka.attribute_selection import ASEvaluation
from weka.attribute_selection import AttributeSelection
# import wekaexamples.helper as helper
from weka.core.classes import Random
from weka.core.converters import Loader
from weka.core.dataset import Instances
from weka.filters import Filter

from weka.core.packages import install_missing_packages, LATEST
from miner.utilities.constants import (
    models_directory,
    packages_directory)
import os
import pprint

def remove_uuid(data):
    remove = Filter(
        classname="weka.filters.unsupervised.attribute.Remove",
        options=["-R", "first"])
    remove.inputformat(data)
    return remove.filter(data)


def nominalize(data):
    nominalize = Filter(
        classname="weka.filters.unsupervised.attribute.NumericToNominal",
        options=["-R", "19"])
    nominalize.inputformat(data)
    return nominalize.filter(data)


def create_model(model_arff, options, filename):
    jvm.start(packages=True, max_heap_size="5028m")

    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    model_data = loader.load_file(model_arff)
    model_data = remove_uuid(model_data)
    model_data = nominalize(model_data)
    model_data.class_is_last()
    classifier = Classifier(classname="weka.classifiers.meta.AttributeSelectedClassifier")
    search = ASSearch(classname="weka.attributeSelection.BestFirst", options=["-D", "1", "-N", "3"])
    evaluator = ASEvaluation(classname="weka.attributeSelection.CfsSubsetEval", options=["-P", "1", "-E", "1"])
    base = Classifier(classname="weka.classifiers.functions.SMO", options=options)

    classifier.set_property("classifier", base.jobject)
    classifier.set_property("evaluator", evaluator.jobject)
    classifier.set_property("search", search.jobject)

    classifier.build_classifier(model_data)
    filename = "test_models/{}.model".format(filename)
    serialization.write(filename, classifier)
    jvm.stop()
    print("Model Created Successfully.")
    print("Filename: {}".format(filename))

def evaluate_all(arff_list, venue_code, grade_name):
    print("evaluate all()")
    print(arff_list)
    print(venue_code)
    print(grade_name)
    start_jvm()
    for arff_file in arff_list:
        evaluate_single(arff_file)
    jvm.stop()

def get_prediction_object(filename):
    arff_file = open(filename, "r")
    prediction_object = {
        "lines": [],
        "uuids": []
    }
    i = 0
    for line in arff_file:
        print(line)
        if len(line) > 100:
            split_line = line.split(",")
            prediction_object["lines"].append(i)
            prediction_object["uuids"].append(split_line[0])
            i += 1
    print(prediction_object)
    return prediction_object

def get_prediction_list(cls, data, lines):
    prediction_list = []
    for index, inst in enumerate(data):
        if index in lines:
            prediction_list.append(cls.classify_instance(inst))
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

def evaluate_single(arff_file):
    race_key = arff_file.replace("arff/", "").replace(".arff", "")
    scheduled_data = build_scheduled_data(arff_file)
    # model_names = ["libsvm", "J48_C0_75"]
    model_name ='smo'
    prediction_object = get_prediction_object(arff_file)
    prediction_object['predictions'] = {}
    filename = "test_models/{}_{}_090.model".format(race_key, model_name)
    try:
        model = Classifier(jobject=serialization.read(filename))
    except:
        print("No model found: {}".format(race_key))
    if model:
        prediction_object['predictions'][model_name] = get_prediction_list(
        model,
        scheduled_data,
        prediction_object["lines"])
    save_all_predictions(
        prediction_object['uuids'],
        prediction_object['predictions'])
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(prediction_object)
    # print("\n", file=analysis_file)
    # print(race_key, file=analysis_file)
    # print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------", file=analysis_file)
    # do_something(prediction_object, model_names, race_key, analysis_file)

def start_jvm():
    jvm.start(packages=True, max_heap_size="6048m")
    install_missing_packages([
        ('LibSVM', LATEST),
        ('LibLINEAR', LATEST)])

def save_all_predictions(uuids, predictions):
    print("save all predictions")
    print(len(uuids))
    for uuid in uuids:
        save_predictions(uuid, predictions, uuids.index(uuid))


def save_predictions(participant_id, predictions, index):
    print("save predictions")
    participant = Participant.objects.get(uuid=participant_id)
    pred = get_prediction(participant)

    for model_name in predictions.keys():
        print(model_name)
        if 'J48' in model_name:
            print("j48")
            print(predictions[model_name][index])
            pred.j48 = predictions[model_name][index]
        elif 'libsvm' in model_name:
            print("libsvm")
            print(predictions[model_name][index])
            pred.lib_svm = predictions[model_name][index]
        elif 'smo' in model_name:
            pred.smo = predictions[model_name][index]
    pred.save()
