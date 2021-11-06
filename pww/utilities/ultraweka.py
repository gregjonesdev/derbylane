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






def create_model(model_arff, classifier, options, filename):
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    model_data = loader.load_file(model_arff)
    model_data = remove_uuid(model_data)
    model_data = nominalize(model_data)
    model_data.class_is_last()


    classifier = Classifier(classname="weka.classifiers.meta.AttributeSelectedClassifier")
    search = ASSearch(classname="weka.attributeSelection.BestFirst", options=["-D", "1", "-N", "3"])
    evaluator = ASEvaluation(classname="weka.attributeSelection.CfsSubsetEval", options=["-P", "1", "-E", "1"])
    base = Classifier(classname="weka.classifiers.functions.SMO")

    classifier.set_property("classifier", base.jobject)
    classifier.set_property("evaluator", evaluator.jobject)
    classifier.set_property("search", search.jobject)

def add_options(options):

    # kernel = Kernel(classname="weka.classifiers.functions.supportVector.RBFKernel", options=["-G", "0.001"])
    classifier = KernelClassifier(classname="weka.classifiers.functions.SMO", options=["-M"])
