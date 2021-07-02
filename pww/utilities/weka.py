import os

from django.core.management.base import BaseCommand
from weka.filters import Filter
import weka.core.jvm as jvm
import weka.core.converters as conv
import weka.core.serialization as serialization
from rawdat.models import Participant
from weka.classifiers import Evaluation, Classifier, FilteredClassifier
from weka.core.classes import Random
from django.core.exceptions import ObjectDoesNotExist
from pww.models import Prediction

confidence_vector = "0.3"
# data_dir = "./rawdat/arff/"

classifiers = [
    # "weka.classifiers.functions.SMO",
    # "weka.classifiers.trees.J48",
    "weka.classifiers.rules.ZeroR",
    "weka.classifiers.functions.SMOreg",
    "weka.classifiers.trees.REPTree",
    "weka.clusterers.SimpleKMeans",
    ]


def create_model(model_arff, race_key):
    jvm.start(packages=True, max_heap_size="2048m")
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    unfiltered_data = loader.load_file(model_arff)
    remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "first"])
    remove.inputformat(unfiltered_data)
    filtered_data = remove.filter(unfiltered_data)
    filtered_data.class_is_last()
    cls = Classifier(classname="weka.classifiers.functions.SMOreg", options=[])
    cls.build_classifier(filtered_data)
    filename = "arff/{}.model".format(race_key)
    serialization.write(filename, cls)
    jvm.stop()

def predict_all(scheduled_data):
    jvm.start(packages=True, max_heap_size="2048m")
    print("weka: predict all")
    for race_key in scheduled_data:
        predict(race_key, scheduled_data[race_key])
    jvm.stop()


def predict(race_key, arff_data):

    filename = "arff/{}.model".format(race_key)
    uuid_list = get_uuid_list(arff_data)
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    scheduled_data = loader.load_file(arff_data)
    remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "first"])
    remove.inputformat(scheduled_data)
    filtered_scheduled = remove.filter(scheduled_data)
    try:
        model = Classifier(jobject=serialization.read(filename))
        make_predictions(model, filtered_scheduled, uuid_list)
    except:
        pass

def evaluate_predictions(cls, data):
    participant_count = 0
    bet_count = 0


    data.class_is_last()
    for index, inst in enumerate(data):
        pred = cls.classify_instance(inst)


def make_predictions(cls, data, uuid_list):
    data.class_is_last()
    for index, inst in enumerate(data):
        pred = cls.classify_instance(inst)
        save_prediction(
            Participant.objects.get(uuid=uuid_list[index]),
            pred
        )

def save_prediction(participant, pred):
    try:
        prediction = Prediction.objects.get(participant=participant)
    except ObjectDoesNotExist:
        new_prediction = Prediction(
            participant = participant
        )
        new_prediction.set_fields_to_base()
        new_prediction.save()
        prediction = new_prediction
    prediction.smo = pred
    prediction.save()
    print("Race {}\t{}:\t{}".format(
        participant.race.number,
        participant.dog.name[:8],
        pred))


def get_uuid_list(filename):
    arff_file = open(filename, "r")
    uuids = []
    for line in arff_file:
        if len(line) > 100:
            uuids.append(line.split(",")[0])
    return uuids
