import weka.core.serialization as serialization
import weka.core.jvm as jvm

from django.core.exceptions import ObjectDoesNotExist

from weka.classifiers import Classifier
from weka.core.converters import Loader
from weka.filters import Filter

from rawdat.models import Participant
from pww.models import Participant_Prediction

from pww.utilities.urls import model_directory

def start_jvm():
    jvm.start(
    packages=True,
    max_heap_size="5028m"
    )

def stop_jvm():
    jvm.stop()


def get_filtered_data(loaded_data, is_nominal):
    filtered_data = remove_uuid(loaded_data)
    filtered_data.class_is_last()
    if is_nominal:
        return nominalize(filtered_data)
    return filtered_data

def get_model(model_directory, model_name):
    filename = get_filename(model_directory, model_name)
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

def build_prediction_object(filtered_data, uuid_line_index, classifier):
    prediction_object = {}
    for index, inst in enumerate(filtered_data):
        if index in uuid_line_index.keys():
            uuid = uuid_line_index[index]
            prediction = classifier.classify_instance(inst)
            prediction_object[uuid] = prediction
    return prediction_object

def get_prediction(participant, weka_model):
    try:
        pred = Participant_Prediction.objects.get(
            participant=participant,
            model=weka_model)
    except ObjectDoesNotExist:
        new_pred = Participant_Prediction(
            participant = participant,
            model = weka_model
        )
        new_pred.set_fields_to_base()
        new_pred.save()
        pred = new_pred
    return pred

def save_predictions(prediction_object, weka_model):
    for uuid in prediction_object.keys():
        prediction = get_prediction(
            Participant.objects.get(uuid=uuid),
            weka_model)
        prediction.smoreg = prediction_object[uuid]
        prediction.save()

def make_predictions(weka_model, prediction_arff, is_nominal):
    uuid_line_index = get_uuid_line_index(prediction_arff)
    loader = Loader(classname="weka.core.converters.ArffLoader")
    loaded_data = loader.load_file(prediction_arff)
    filtered_data = get_filtered_data(loaded_data, is_nominal)
    model_filename = get_model(model_directory, weka_model.get_name())
    prediction_object = build_prediction_object(
        filtered_data,
        uuid_line_index,
        model_filename)
    save_predictions(prediction_object, weka_model)
