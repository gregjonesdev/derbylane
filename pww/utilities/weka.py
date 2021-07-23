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
import pprint

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
    print("predict all")
    print(arff_list)
    start_jvm()
    analysis_file = open("prediction_analysis.txt", "w")
    for arff_file in arff_list:
        predict_single(arff_file, analysis_file)
    analysis_file.close()
    # print("Results written to {}".format(analysis_file.name))
    jvm.stop()

def predict_single(arff_file, analysis_file):
    print("predict single ()")
    race_key = arff_file.split("/")
    race_key = arff_file.replace("arff/", "").replace(".arff", "")
    scheduled_data = build_scheduled_data(arff_file)


    race_key = "WD_548_AA"

    model_names = ["libsvm", "J48_C0_75"]
    predict(race_key, arff_file, analysis_file, scheduled_data, model_names)

def build_scheduled_data(arff_data):
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    loaded_data = loader.load_file(arff_data)
    scheduled_data = remove_uuid(loaded_data)
    scheduled_data = nominalize(scheduled_data)
    scheduled_data.class_is_last()
    return scheduled_data



def predict(race_key, arff_data, analysis_file, scheduled_data, model_names):
    print("predicting: {}".format(race_key))

    prediction_object = get_prediction_object(arff_data)
    prediction_object['predictions'] = {}

    for model_name in model_names:
        filename = "weka_models/{}_{}.model".format(race_key, model_name)

        try:
            print("Looking for {}".format(filename))
            model = Classifier(jobject=serialization.read(filename))
            prediction_object['predictions'][model_name] = get_prediction_list(
                model,
                scheduled_data,
                prediction_object["lines"])
            # prediction_tuple = get_prediction_tuple(model, scheduled_data, uuid_tuple, race_key, arff_data)
        except:
            print("No model found: {}".format(race_key))

    # print(prediction_object)

    pp = pprint.PrettyPrinter(indent=4)

    pp.pprint(prediction_object)
    save_all_predictions(
        prediction_object['uuids'],
        prediction_object['predictions'])


def save_all_predictions(uuids, predictions):
    for uuid in uuids:
        save_predictions(uuid, predictions, uuids.index(uuid))



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
    # print("GPW")
    # print(prediction)
    prediction_winnings = {
        'bet_count': 0,
        'win': 0,
        'place': 0,
        'show': 0,
    }
    for entry in prediction_tuple:
        # print("A")
        participant = Participant.objects.get(uuid=entry[0])
        # print("{} ({})".format(entry[1], type(entry[1])))
        # print("{} ({})".format(prediction, type(prediction)))
    #
        if int(entry[1]) == prediction:
            prediction_winnings['bet_count'] += 1
            prediction_winnings['win'] += get_win_bet_earnings(participant)
            prediction_winnings['place'] += get_place_bet_earnings(participant)
            prediction_winnings['show'] += get_show_bet_earnings(participant)
            # raise SystemExit(0)
    return prediction_winnings

eval_string = "{}\t\t{}\t\t{}\t\t{}"
bet_amount = 2

def evaluate_predictions(prediction_tuple, filename, analysis_file):
    print("{}\n".format(filename), file=analysis_file)
    print(eval_string.format(
    "",
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


def new_evaluate_predictions(prediction_tuple, table_name, analysis_file, i):
    # print("{}\n".format(filename), file=analysis_file)
    # print(eval_string.format(
    # "",
    # "Win",
    # "Place",
    # "Show"
    # ), file=analysis_file)
    # print("A")
    # print(prediction_tuple)
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
    print(breakdown_string.format(
        table_name.replace("EAR", ""),
        "%",
        "\t{}".format(win_winnings),
        "\t{}".format(place_winnings),
        "\t{}".format(show_winnings)
    ))
        # print(eval_string.format(
        # i,
        # win_winnings,
        # place_winnings,
        # show_winnings
        # ), file=analysis_file)

def start_jvm():
    jvm.start(packages=True, max_heap_size="2048m")
    install_missing_packages([
        ('LibSVM', LATEST),
        ('LibLINEAR', LATEST)])


def compare_predictions(arff_file):
    print("Currently disabled: No rpd()")
    race_key = "SL_583_C"
    print("weka compare")
    print(models_directory)
    start_jvm()
    analysis_file = open("{}_comparison.txt".format(race_key), "w")
    uuid_tuple = get_prediction_object(arff_file)
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    test_data = loader.load_file(arff_file)
    test_data = remove_uuid(test_data)
    test_data = nominalize(test_data)
    test_data.class_is_last()
    skip_models = ["SL_583_C_model_SMO_C_8_0.model"]
    single_model = ['SMO_C_4_0']
    for i in range(4):
        print("\nBets on Prediction: {}\n".format(i))
        print(breakdown_string.format(
            "Model",
            "\t% Correct",
            "Win",
            "\tPlace",
            "\tShow"
        ))
        for model_name in os.listdir(models_directory):
            if not model_name in skip_models:
                if 'SMO' in model_name:
                    pass
                    # retrieve_prediction_data(model_name, race_key, test_data, uuid_tuple, analysis_file, i)
    analysis_file.close()
    jvm.stop()
    # print("\nResults written to {}\n".format(analysis_file.name))

breakdown_string = "{}\t\t{}\t{}\t\t{}\t\t{}"


# def retrieve_prediction_data(model_name, race_key, test_data, uuid_tuple, analysis_file, i):
#     # print("RPD")
#     short_name = model_name.replace("{}_model_".format(race_key), "")
#     # print("\n-----------------------------------")
#     table_name = short_name.replace(".model", "")
#     # print("-----------------------------------\n")
#
#     # print(model_name)
#     # print(len(test_data))
#     # print(uuid_tuple[:5])
#     prediction_data = []
#
#     model_location = "{}/{}".format(models_directory, model_name)
#     model = Classifier(jobject=serialization.read(model_location))
#     prediction_tuple = get_prediction_tuple(model, test_data, uuid_tuple)
#     # print(table_name)
#     # for each in prediction_tuple[:50]:
#     #     print(type(each[1]))
#     # print(prediction_tuple)
#     new_evaluate_predictions(prediction_tuple, table_name, analysis_file, i)




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



def get_prediction_tuple(cls, data, uuid_tuple, race_key, arff_data):
    print("GPT")
    # raise SystemExit(0)
    print(arff_data)
    filename = "weka_models/{}_libsvm.model".format(race_key)
    prediction_object = get_prediction_object(arff_data)

    # try:
    #     model = Classifier(jobject=serialization.read(filename))
    #     prediction_tuple = []
    #     prediction_obj['lib_svm'] = []
    #     prediction_obj['j48'] = []
    #     prediction_list = get_prediction_list(cls, data)
    #     i = 0
    #     while i < len(uuid_tuple):
    #         prediction_tuple.append((uuid_tuple[i][1], prediction_list[i]))
    #         i += 1
    #     return prediction_tuple
    #
    # except:
    #     print("No model found: {}".format(race_key))

    #
    #
    # prediction_list = get_prediction_list(cls, data)
    # i = 0
    # while i < len(uuid_tuple):
    #     prediction_tuple.append((uuid_tuple[i][1], prediction_list[i]))
    #     i += 1
    # return prediction_tuple

def convert_to_list(weka_dataset):
    list = []
    for inst in enumerate(weka_dataset):
        list.append(inst)
    return list


def get_prediction_list(cls, data, lines):
    prediction_list = []
    for index, inst in enumerate(data):
        if index in lines:
            prediction_list.append(cls.classify_instance(inst))
    return prediction_list

def save_libsvm_predictions(prediction_tuple):
    for each in prediction_tuple:
        participant = Participant.objects.get(uuid=each[0])
        save_libsvm_prediction(participant, each[1])

def save_predictions(participant_id, predictions, index):
    try:
        pred = Prediction.objects.get(participant_id=participant_id)
    except ObjectDoesNotExist:
        new_pred = Prediction(
            participant = participant
        )
        new_pred.set_fields_to_base()
        new_pred.save()
        pred = new_prediction

    for prediction in predictions:
        if 'J48' in prediction:
            print("save j48")
            print(prediction)
            pred.j48 = predictions[prediction][index]
        elif 'libsvm' in prediction:
            print("save libsvm")
            pred.lib_svm = predictions[prediction][index]
    pred.save()


def get_prediction_object(filename):
    arff_file = open(filename, "r")
    prediction_object = {
        "lines": [],
        "uuids": []
    }
    i = 0
    for line in arff_file:
        if len(line) > 100:
            split_line = line.split(",")
            if split_line[19] == "?\n":
                prediction_object["lines"].append(i)
                prediction_object["uuids"].append(split_line[0])
            i += 1
    return prediction_object
