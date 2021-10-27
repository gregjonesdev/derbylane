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



    cls = Classifier(classname=classifier, options=options)
    cls.build_classifier(model_data)
    filename = "test_models/{}.model".format(filename)
    print("filename: {}".format(filename))
    serialization.write(filename, cls)


def predict_all(arff_list):
    start_jvm()
    for arff_file in arff_list:
        predict_single(arff_file)
    jvm.stop()


def evaluate_all(arff_list, venue_code, grade_name):
    print("evaluate all")
    start_jvm()
    analysis_file = open("prediction_analysis_{}_{}.txt".format(
        venue_code,
        grade_name
    ), "w")
    for arff_file in arff_list:
        # predict_single(arff_file)
        evaluate_single(arff_file, analysis_file)
    analysis_file.close()
    jvm.stop()


def evaluate_single(arff_file, analysis_file):
    race_key = arff_file.replace("arff/", "").replace(".arff", "")
    scheduled_data = build_scheduled_data(arff_file)
    model_names = ["libsvm", "J48_C0_75"]
    # if race_key == "WD_548_AA":
    evaluate(race_key, arff_file, analysis_file, scheduled_data, model_names)


def predict_single(arff_file):
    race_key = arff_file.replace("arff/", "").replace(".arff", "")
    scheduled_data = build_scheduled_data(arff_file)
    model_names = ["libsvm", "J48_C0_75"]
    # model_names = ["libsvm"]
    # model_names = ["J48_C0_75"]
    race_key == "WD_548_AA"
    make_prediction(race_key, arff_file, scheduled_data, model_names)

def build_scheduled_data(arff_data):
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    loaded_data = loader.load_file(arff_data)
    scheduled_data = remove_uuid(loaded_data)
    scheduled_data = nominalize(scheduled_data)
    scheduled_data.class_is_last()
    print(scheduled_data)



    # New
    # example(scheduled_data)




    #
    #
    # search = ASSearch(classname="weka.attributeSelection.BestFirst", options=["-D", "1", "-N", "3"])
    # evaluator = ASEvaluation(classname="weka.attributeSelection.CfsSubsetEval", options=["-P", "1", "-E", "1"])
    #
    # "weka.attributeSelection.WrapperSubsetEval -B"
    #
    # attsel = AttributeSelection()
    # attsel.search(search)
    # attsel.evaluator(evaluator)
    # attsel.select_attributes(scheduled_data)
    #
    #
    # print("# attributes: " + str(attsel.number_attributes_selected))
    # print("attributes: " + str(attsel.selected_attributes))
    # print("result string:\n" + attsel.results_string)
    return scheduled_data

def example(data):
    print("example")
    classifier = Classifier(classname="weka.classifiers.trees.J48")

    # randomize data
    folds = 10
    seed = 1
    rnd = Random(seed)
    rand_data = Instances.copy_instances(data)
    rand_data.randomize(rnd)
    if rand_data.class_attribute.is_nominal:
        rand_data.stratify(folds)

    # perform cross-validation and add predictions
    predicted_data = None
    evaluation = Evaluation(rand_data)
    for i in range(folds):
        train = rand_data.train_cv(folds, i)
        # the above code is used by the StratifiedRemoveFolds filter,
        # the following code is used by the Explorer/Experimenter
        # train = rand_data.train_cv(folds, i, rnd)
        test = rand_data.test_cv(folds, i)

        # build and evaluate classifier
        cls = Classifier.make_copy(classifier)
        cls.build_classifier(train)
        evaluation.test_model(cls, test)

        # add predictions
        addcls = Filter(
            classname="weka.filters.supervised.attribute.AddClassification",
            options=["-classification", "-distribution", "-error"])
        # setting the java object directory avoids issues with correct quoting in option array
        addcls.set_property("classifier", Classifier.make_copy(classifier))
        addcls.inputformat(train)
        addcls.filter(train)  # trains the classifier
        pred = addcls.filter(test)
        if predicted_data is None:
            predicted_data = Instances.template_instances(pred, 0)
        for n in range(pred.num_instances):
            predicted_data.add_instance(pred.get_instance(n))

    print("")
    print("=== Setup ===")
    print("Classifier: " + classifier.to_commandline())
    print("Dataset: " + data.relationname)
    print("Folds: " + str(folds))
    print("Seed: " + str(seed))
    print("")
    print(evaluation.summary("=== " + str(folds) + " -fold Cross-Validation ==="))
    print("")
    print(predicted_data)



def evaluate(race_key, arff_data, analysis_file, scheduled_data, model_names):
    print("evaluate()")
    # print(analysis_file.name)
    prediction_object = get_prediction_object(arff_data)
    prediction_object['predictions'] = {}
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(prediction_object)

    for model_name in model_names:
        model = None
        filename = "weka_models/{}_{}.model".format(race_key, model_name)
        try:
            model = Classifier(jobject=serialization.read(filename))
        except:
            print("No model found: {}".format(race_key))
        if model:
            prediction_object['predictions'][model_name] = get_prediction_list(
            model,
            scheduled_data,
            prediction_object["lines"])
    # save_all_predictions(
    #     prediction_object['uuids'],
    #     prediction_object['predictions'])
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(prediction_object)
    # print("\n", file=analysis_file)
    # print(race_key, file=analysis_file)
    # print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------", file=analysis_file)
    do_something(prediction_object, model_names, race_key, analysis_file)

def do_something(prediction_object, model_names, race_key, analysis_file):
    x_label = model_names[0].upper()
    y_label = model_names[1].upper()


    filtered_predictions = get_filtered_predicitions(prediction_object['uuids'])
    # print(len(filtered_predictions))
    build_matrix_shell("Win", x_label, y_label, get_win_bet_earnings, race_key, analysis_file, filtered_predictions)
    build_matrix_shell("Place", x_label, y_label, get_place_bet_earnings, race_key, analysis_file, filtered_predictions)
    build_matrix_shell("Show", x_label, y_label, get_show_bet_earnings, race_key, analysis_file, filtered_predictions)

    # print("\n", file=analysis_file)
    # print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------", file=analysis_file)
    example_calculation()

eval_string = "{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}"

def build_matrix_shell(title, x_label, y_label, get_bet_earnings, race_key, analysis_file, filtered_predictions):

    print("\nAverage Return for $2.00 {} Bets:".format(title), file=analysis_file)
    print("\t\t\t\t\t\t\t\t\t{}".format(x_label), file=analysis_file)
    prediction_max = 8
    i = 0
    print(eval_string.format("\t", " ", "0\t", "1\t", "2\t", "3\t", "4\t", "5\t", "6\t", "7"), file=analysis_file)
    while i <= prediction_max:
        write_matrix_row(i, y_label, get_bet_earnings, race_key, analysis_file, filtered_predictions)

        i += 1



def write_matrix_row(y_value, y_label, get_bet_earnings, race_key, analysis_file, filtered_predictions):
    if y_value == 4:
        cell_0 = "{}".format(y_label)
    else:
        cell_0 = "\t"
    x_value_list = get_x_value_list(y_value, get_bet_earnings, race_key, filtered_predictions)
    print(eval_string.format(
        cell_0,
        y_value,
        x_value_list[0],
        x_value_list[1],
        x_value_list[2],
        x_value_list[3],
        x_value_list[4],
        x_value_list[5],
        x_value_list[6],
        x_value_list[7]), file=analysis_file)

def get_dollars(number):
    return "${}".format(round(number, 2))

def get_x_value_list(y_value, get_bet_earnings, race_key, filtered_predictions):
    x_value_list = []
    split_race_key = race_key.split("_") # ['WD', '548', 'AA']

    # x: libsvm
    # y: j48
    i = 0
    while i <=7:
        specific_predictions = filtered_predictions.filter(
            lib_svm=i,
            j48=y_value
        )
        count = specific_predictions.count()
        winnings = 0
        for prediction in specific_predictions:
            winnings += get_bet_earnings(prediction.participant)
        if count > 0:
            x_value_list.append("{} ({})".format(get_dollars(winnings/count), count))
        else:
            x_value_list.append("--------")
        i += 1
    # x_value_list = [ 0.65, 0.75, 0.85, 1.2, 0.65, 0.75, 0.85, 1.2]
    return x_value_list

def example_calculation():
    pass
    # filtered_predictions = get_filtered_predicitions(1, 1)
    # count = filtered_predictions.count()
    # win_winnings = 0
    # for prediction in filtered_predictions:
    #     win_winnings += get_win_bet_earnings(prediction.participant)
    # total = get_dollars(win_winnings)
    # print("Sample Calculation for libsvm = 1 and j48 = 1")
    # print("Total win bet earnings: {}".format(total))
    # print("Total win bets placed: {}".format(count))
    #
    # print("{} / {} = {}/bet".format(total, count, get_dollars(win_winnings/count)))


def get_filtered_predicitions(participant_uuids):
    return Prediction.objects.filter(
        participant__in=participant_uuids
    )


def make_prediction(race_key, arff_data, scheduled_data, model_names):
    prediction_object = get_prediction_object(arff_data)

    prediction_object['predictions'] = {}
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(prediction_object)
    print(scheduled_data)
    for model_name in model_names:
        model = None
        race_key = "WD_548_AA"
        filename = "weka_models/{}_{}.model".format(race_key, model_name)
        try:
            model = Classifier(jobject=serialization.read(filename))
        except:
            print("No model found: {}".format(race_key))
        if model:
            prediction_object['predictions'][model_name] = get_prediction_list(
            model,
            scheduled_data,
            prediction_object["lines"])
    print(prediction_object)

    save_all_predictions(
        prediction_object['uuids'],
        prediction_object['predictions'])


def save_all_predictions(uuids, predictions):
    print("save all predictions")
    print(len(uuids))
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
#
# def get_prediction_winnings(prediction_tuple, prediction):
#     # print("GPW")
#     # print(prediction)
#     prediction_winnings = {
#         'bet_count': 0,
#         'win': 0,
#         'place': 0,
#         'show': 0,
#     }
#     for entry in prediction_tuple:
#         # print("A")
#         participant = Participant.objects.get(uuid=entry[0])
#         # print("{} ({})".format(entry[1], type(entry[1])))
#         # print("{} ({})".format(prediction, type(prediction)))
#     #
#         if int(entry[1]) == prediction:
#             prediction_winnings['bet_count'] += 1
#             prediction_winnings['win'] += get_win_bet_earnings(participant)
#             prediction_winnings['place'] += get_place_bet_earnings(participant)
#             prediction_winnings['show'] += get_show_bet_earnings(participant)
#             # raise SystemExit(0)
#     return prediction_winnings
#
# eval_string = "{}\t\t{}\t\t{}\t\t{}"
# bet_amount = 2
#
# def evaluate_predictions(prediction_tuple, filename, analysis_file):
#     print("{}\n".format(filename), file=analysis_file)
#     print(eval_string.format(
#     "",
#     "Win",
#     "Place",
#     "Show"
#     ), file=analysis_file)
#     i = 0
#     for i in range(9):
#         prediction_winnings = get_prediction_winnings(prediction_tuple, i)
#         bet_count = prediction_winnings["bet_count"]
#         if bet_count > 0:
#             win_winnings = "${}".format(
#                 round(prediction_winnings["win"]/(bet_count*2), 2))
#             place_winnings = "${}".format(
#                 round(prediction_winnings["place"]/(bet_count*2), 2))
#             show_winnings = "${}".format(
#                 round(prediction_winnings["show"]/(bet_count*2), 2))
#         else:
#             win_winnings = "--"
#             place_winnings = "--"
#             show_winnings = "--"
#         print(eval_string.format(
#         i,
#         win_winnings,
#         place_winnings,
#         show_winnings
#         ), file=analysis_file)
#
#
# def new_evaluate_predictions(prediction_tuple, table_name, analysis_file, i):
#     # print("{}\n".format(filename), file=analysis_file)
#     # print(eval_string.format(
#     # "",
#     # "Win",
#     # "Place",
#     # "Show"
#     # ), file=analysis_file)
#     # print("A")
#     # print(prediction_tuple)
#     prediction_winnings = get_prediction_winnings(prediction_tuple, i)
#     bet_count = prediction_winnings["bet_count"]
#     if bet_count > 0:
#         win_winnings = "${}".format(
#             round(prediction_winnings["win"]/(bet_count*2), 2))
#         place_winnings = "${}".format(
#             round(prediction_winnings["place"]/(bet_count*2), 2))
#         show_winnings = "${}".format(
#             round(prediction_winnings["show"]/(bet_count*2), 2))
#     else:
#         win_winnings = "--"
#         place_winnings = "--"
#         show_winnings = "--"
#     print(breakdown_string.format(
#         table_name.replace("EAR", ""),
#         "%",
#         "\t{}".format(win_winnings),
#         "\t{}".format(place_winnings),
#         "\t{}".format(show_winnings)
#     ))
#         # print(eval_string.format(
#         # i,
#         # win_winnings,
#         # place_winnings,
#         # show_winnings
#         # ), file=analysis_file)
#
def start_jvm():
    jvm.start(packages=True, max_heap_size="6048m")
    install_missing_packages([
        ('LibSVM', LATEST),
        ('LibLINEAR', LATEST)])
#
#
# def compare_predictions(arff_file):
#     print("Currently disabled: No rpd()")
#     race_key = "SL_583_C"
#     print("weka compare")
#     print(models_directory)
#     start_jvm()
#     analysis_file = open("{}_comparison.txt".format(race_key), "w")
#     uuid_tuple = get_prediction_object(arff_file)
#     loader = conv.Loader(classname="weka.core.converters.ArffLoader")
#     test_data = loader.load_file(arff_file)
#     test_data = remove_uuid(test_data)
#     test_data = nominalize(test_data)
#     test_data.class_is_last()
#     skip_models = ["SL_583_C_model_SMO_C_8_0.model"]
#     single_model = ['SMO_C_4_0']
#     for i in range(4):
#         print("\nBets on Prediction: {}\n".format(i))
#         print(breakdown_string.format(
#             "Model",
#             "\t% Correct",
#             "Win",
#             "\tPlace",
#             "\tShow"
#         ))
#         for model_name in os.listdir(models_directory):
#             if not model_name in skip_models:
#                 if 'SMO' in model_name:
#                     pass
#                     # retrieve_prediction_data(model_name, race_key, test_data, uuid_tuple, analysis_file, i)
#     analysis_file.close()
#     jvm.stop()
#     # print("\nResults written to {}\n".format(analysis_file.name))
#
# breakdown_string = "{}\t\t{}\t{}\t\t{}\t\t{}"
#
#
# # def retrieve_prediction_data(model_name, race_key, test_data, uuid_tuple, analysis_file, i):
# #     # print("RPD")
# #     short_name = model_name.replace("{}_model_".format(race_key), "")
# #     # print("\n-----------------------------------")
# #     table_name = short_name.replace(".model", "")
# #     # print("-----------------------------------\n")
# #
# #     # print(model_name)
# #     # print(len(test_data))
# #     # print(uuid_tuple[:5])
# #     prediction_data = []
# #
# #     model_location = "{}/{}".format(models_directory, model_name)
# #     model = Classifier(jobject=serialization.read(model_location))
# #     prediction_tuple = get_prediction_tuple(model, test_data, uuid_tuple)
# #     # print(table_name)
# #     # for each in prediction_tuple[:50]:
# #     #     print(type(each[1]))
# #     # print(prediction_tuple)
# #     new_evaluate_predictions(prediction_tuple, table_name, analysis_file, i)
#
#
#
#
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
#
#
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

def save_predictions(participant_id, predictions, index):
    print("save predictions")
    participant = Participant.objects.get(uuid=participant_id)
    pred = get_prediction(participant)
    print(predictions)
    print(participant)
    print(index)
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
    pred.save()

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


# def get_prediction_object(filename):
#     arff_file = open(filename, "r")
#     prediction_object = {
#         "lines": [],
#         "uuids": []
#     }
#     i = 0
#     for line in arff_file:
#         # print(len(line))
#         if len(line) > 100:
#             split_line = line.split(",")
#             print(len(split_line))
#             print(split_line[19])
#             if split_line[19] == "?\n":
#                 prediction_object["lines"].append(i)
#                 prediction_object["uuids"].append(split_line[0])
#             i += 1
#     print(prediction_object)
#     raise SystemExit(0)
#     return prediction_object
