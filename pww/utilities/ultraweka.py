from pww.utilities.classifiers import classifiers

from weka.attribute_selection import ASSearch
from weka.attribute_selection import ASEvaluation
from weka.attribute_selection import AttributeSelection
from weka.core.converters import Loader
from weka.filters import Filter

def nominalize(data):
    nominalize = Filter(
        classname="weka.filters.unsupervised.attribute.NumericToNominal",
        options=["-R", "{}".format(csv_columns.index('Fi'))])
    nominalize.inputformat(data)
    return nominalize.filter(data)

def get_selected_attributes():
    attsel = AttributeSelection()
    search = ASSearch(
        classname="weka.attributeSelection.BestFirst",
        options=["-D", "1", "-N", "5"])
    evaluation = ASEvaluation(
        classname="weka.attributeSelection.CfsSubsetEval",
        options=["-P", "1", "-E", "1"])
    attsel.search(search)
    attsel.evaluator(evaluation)
    return attsel

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

    selected_attributes = get_selected_attributes()
    selected_attributes.build_classifier(filtered_data)
    serialization.write(filename, selected_attributes)
    return Classifier(jobject=serialization.read(filename))


def remove_uuid(data):
    remove = Filter(
        classname="weka.filters.unsupervised.attribute.Remove",
        options=["-R", "first"])
    remove.inputformat(data)
    return remove.filter(data)
