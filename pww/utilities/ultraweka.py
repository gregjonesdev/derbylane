from pww.utilities.classifiers import classifiers
from weka.attribute_selection import ASSearch
from weka.attribute_selection import ASEvaluation
from weka.attribute_selection import AttributeSelection
from weka.classifiers import Classifier
from weka.core.converters import Loader
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

def get_loaded_data(training_arff):
    loader = Loader(classname="weka.core.converters.ArffLoader")
    return loader.load_file(training_arff)

def get_classifier(training_arff, classifier_attributes):
    filename = "test_models/test.model"
    loaded_data = get_loaded_data(training_arff)
    filtered_data = get_filtered_data(
        loaded_data,
        classifier_attributes["is_nominal"])
    base_classifier = Classifier(
        classname=classifier_attributes["path"],
        options=classifier_attributes["options"])
    attr_classifier = get_attr_classifier(base_classifier)
    attr_classifier.build_classifier(filtered_data)
    serialization.write(filename, attr_classifier)
    return Classifier(jobject=serialization.read(filename))

def remove_uuid(data):
    remove = Filter(
        classname="weka.filters.unsupervised.attribute.Remove",
        options=["-R", "first"])
    remove.inputformat(data)
    return remove.filter(data)
