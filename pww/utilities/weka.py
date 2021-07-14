from django.core.management.base import BaseCommand
from weka.filters import Filter
import weka.core.jvm as jvm
import weka.core.packages as packages
import weka.core.converters as conv
import weka.core.serialization as serialization
from libsvm.svmutil import *
from rawdat.models import Participant
from weka.classifiers import Classifier
from django.core.exceptions import ObjectDoesNotExist
from pww.models import Prediction
from weka.core.packages import install_missing_packages, LATEST
from miner.utilities.constants import (
    models_directory,
    packages_directory)
import os

def create_model(model_arff, classifier, options, filename):
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    model_data = loader.load_file(model_arff)
    model_data = remove_uuid(model_data)
    model_data = nominalize(model_data)
    model_data.class_is_last()
    cls = Classifier(classname=classifier, options=options)
    cls.build_classifier(model_data)
    filename = "test_models/{}.model".format(filename)
    print("filename: {}".format(filename))
    serialization.write(filename, cls)


def predict_all(arff_list):
    jvm.start(packages=True, max_heap_size="2048m")
    analysis_file = open("prediction_analysis.txt", "w")
    for arff_file in arff_list:
        predict_single(arff_file, analysis_file)
    analysis_file.close()
    print("Results written to {}".format(analysis_file.name))
    jvm.stop()

def predict_single(arff_file, analysis_file):
    race_key = arff_file.split("/")
    race_key = arff_file.replace("arff/", "").replace(".arff", "")
    predict(race_key, arff_file, analysis_file)


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
    prediction.j48 = pred
    prediction.save()
    print("Race {}\t{}:\t{}".format(
        participant.race.number,
        participant.dog.name[:8],
        pred))


def predict(race_key, arff_data, analysis_file):
    # filename = "arff/{}.model".format(race_key)
    filename = "weka_models/{}_J48_C0_75.model".format(race_key)
    # uuid_list = get_uuid_list(arff_data)
    uuid_tuple = get_uuid_tuple(arff_data)
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    loaded_data = loader.load_file(arff_data)
    scheduled_data = remove_uuid(loaded_data)
    scheduled_data = nominalize(scheduled_data)
    scheduled_data.class_is_last()
    prediction_tuple = None
    try:
        model = Classifier(jobject=serialization.read(filename))
        prediction_tuple = get_prediction_tuple(model, scheduled_data, uuid_tuple)
    except:
        print("No model found: {}".format(race_key))
    if prediction_tuple:
        evaluate_predictions(prediction_tuple, filename, analysis_file)
        save_predictions(prediction_tuple)

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

def get_prediction_winnings(prediction_tuple, prediction):
    prediction_winnings = {
        'bet_count': 0,
        'win': 0,
        'place': 0,
        'show': 0,
    }
    for entry in prediction_tuple:
        participant = Participant.objects.get(uuid=entry[0])
        if int(entry[1]) == prediction:
            prediction_winnings['bet_count'] += 1
            prediction_winnings['win'] += get_win_bet_earnings(participant)
            prediction_winnings['place'] += get_place_bet_earnings(participant)
            prediction_winnings['show'] += get_show_bet_earnings(participant)
    return prediction_winnings

eval_string = "{}\t\t{}\t\t{}\t\t{}"
bet_amount = 2

def evaluate_predictions(prediction_tuple, filename, analysis_file):
    print("{}\n".format(filename), file=analysis_file)
    print(eval_string.format(
    "J48",
    "Win",
    "Place",
    "Show"
    ), file=analysis_file)
    i = 0
    for i in range(9):
        prediction_winnings = get_prediction_winnings(prediction_tuple, i)
        bet_count = prediction_winnings["bet_count"]
        if bet_count > 0:
            win_winnings = "${}".format(
                round(prediction_winnings["win"]/(bet_count*2), 2))
            place_winnings = "${}".format(
                round(prediction_winnings["place"]/(bet_count*2), 2))
            show_winnings = "${}".format(
                round(prediction_winnings["show"]/(bet_count*2), 2))
        else:
            win_winnings = "--"
            place_winnings = "--"
            show_winnings = "--"
        print(eval_string.format(
        i,
        win_winnings,
        place_winnings,
        show_winnings
        ), file=analysis_file)

def compare_predictions(arff_file):
    race_key = "SL_583_C"
    print("weka compare")
    print(models_directory)
    jvm.start(packages=True, max_heap_size="2048m")
    install_missing_packages([
        ('LibSVM', LATEST),
        ('LibLINEAR', LATEST)])
    print("\n")
    analysis_file = open("{}_comparison.txt".format(race_key), "w")
    uuid_tuple = get_uuid_tuple(arff_file)
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    test_data = loader.load_file(arff_file)
    test_data = remove_uuid(test_data)
    test_data = nominalize(test_data)
    test_data.class_is_last()
    analysis_file
    # print(eval_string.format(
    # "J48",
    # "Win",
    # "Place",
    # "Show"
    # ), file=analysis_file)
    print(breakdown_string.format(
        "Model",
        "% Correct",
        "Win",
        "Place",
        "Show"))
    skip_models = ["SL_583_C_model_SMO_C_8_0.model"]
    for model_name in os.listdir(models_directory):
        if not model_name in skip_models:
            retrieve_prediction_data(model_name, race_key, test_data, uuid_tuple)
    analysis_file.close()
    jvm.stop()
    print("\nResults written to {}\n".format(analysis_file.name))

breakdown_string = "{}\t\t\t{}\t{}\t{}\t\t{}"


def retrieve_prediction_data(model_name, race_key, test_data, uuid_tuple):
    # print("RPD")
    short_name = model_name.replace("{}_model_".format(race_key), "")
    print(short_name)
    # print(model_name)
    # print(len(test_data))
    # print(uuid_tuple[:5])
    prediction_data = []
    # if "svm" in model_name.lower():
        # model = svm_load_model(model_name)
        # print(model)
        # pass

    model_location = "{}/{}".format(models_directory, model_name)
    model = Classifier(jobject=serialization.read(model_location))
    print(get_prediction_tuple(model, test_data, uuid_tuple))
    # ERROR:                  b
    # javabridge.jutil.JavaException:
    # Unable to find class weka.classifiers.functions.LibLINEAR



def get_win_bet_earnings(participant):
    try:
        if participant.final == 1:
            return participant.straight_wager.win
    except:
        pass
    return 0

def get_place_bet_earnings(participant):
    try:
        if participant.final <=2:
            if participant.straight_wager.place:
                return participant.straight_wager.place
    except:
        pass
    return 0

def get_show_bet_earnings(participant):
    try:
        if participant.final <= 3:
            if participant.straight_wager.show:
                return participant.straight_wager.show
        else:
            return 0
    except:
        pass
    return 0


def get_prediction_tuple(cls, data, uuid_tuple):
    # print("GPT")
    prediction_tuple = []
    prediction_list = get_prediction_list(cls, data)
    i = 0
    while i < len(uuid_tuple):
        prediction_tuple.append((uuid_tuple[i][1], prediction_list[i]))
        i += 1
    return prediction_tuple

def get_prediction_list(cls, data):
    prediction_list = []
    for index, inst in enumerate(data):
        prediction_list.append(cls.classify_instance(inst))
    return prediction_list

def save_predictions(prediction_tuple):
    for each in prediction_tuple:
        participant = Participant.objects.get(uuid=each[0])
        save_prediction(participant, each[1])

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
    prediction.j48 = pred
    prediction.save()
    print("Race {}\t{}:\t{}".format(
        participant.race.number,
        participant.dog.name[:8],
        pred))

def get_uuid_tuple(filename):
    arff_file = open(filename, "r")
    uuids = []
    i = 0
    for line in arff_file:
        if len(line) > 100:
            split_line = line.split(",")
            if split_line[19] == "?\n":
                uuids.append([i, split_line[0]])
            i += 1
    return uuids
