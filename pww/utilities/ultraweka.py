from miner.utilities.constants import csv_columns
from pww.utilities.classifiers import classifiers
from weka.attribute_selection import ASSearch
from weka.attribute_selection import ASEvaluation
from weka.attribute_selection import AttributeSelection
from weka.classifiers import Classifier
from weka.filters import Filter

import weka.core.serialization as serialization

def nominalize(data):
    nominalize = Filter(
        classname="weka.filters.unsupervised.attribute.NumericToNominal",
        options=["-R", "{}".format(csv_columns.index('Fi'))])
    nominalize.inputformat(data)
    return nominalize.filter(data)

def get_attr_classifier(base_classifier):
    attr_classifier = Classifier(
        classname="weka.classifiers.meta.AttributeSelectedClassifier")
    search = ASSearch(
        classname="weka.attributeSelection.BestFirst",
        options=["-D", "1", "-N", "3"])
    evaluator = ASEvaluation(
        classname="weka.attributeSelection.CfsSubsetEval",
        options=["-P", "1", "-E", "1"])
    attr_classifier.set_property("classifier", base_classifier.jobject)
    attr_classifier.set_property("evaluator", evaluator.jobject)
    attr_classifier.set_property("search", search.jobject)
    return attr_classifier

def get_filtered_data(loaded_data, is_nominal):
    filtered_data = remove_uuid(loaded_data)
    filtered_data.class_is_last()
    if is_nominal:
        return nominalize(filtered_data)
    return filtered_data

def get_classifier(training_arff, classifier_attributes, loader):
    filename = "test_models/test.model"
    loaded_data = loader.load_file(training_arff)
    filtered_data = get_filtered_data(
        loaded_data,
        classifier_attributes["is_nominal"])
    base_classifier = Classifier(
        classname=classifier_attributes["path"],
        options=classifier_attributes["options"])
    attr_classifier = get_attr_classifier(base_classifier)
    # ERROR: weka.classifiers.trees.J48: Cannot handle numeric class!
    attr_classifier.build_classifier(filtered_data)
    serialization.write(filename, attr_classifier)
    return Classifier(jobject=serialization.read(filename))

def remove_uuid(data):
    remove = Filter(
        classname="weka.filters.unsupervised.attribute.Remove",
        options=["-R", "first"])
    remove.inputformat(data)
    return remove.filter(data)

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


def get_predictions(testing_arff, classifier, loader, is_nominal):
    uuid_line_index = get_uuid_line_index(testing_arff)
    loaded_data = loader.load_file(testing_arff)
    filtered_data = get_filtered_data(loaded_data, is_nominal)
    for index, inst in enumerate(filtered_data):
        if index in uuid_line_index.keys():
            uuid = uuid_line_index[index]
            prediction = classifier.classify_instance(inst)
            print("{}: {}".format(uuid, prediction))
            dist = classifier.distribution_for_instance(inst)
            print(dist)
            print("----")
