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

breakdown_string="{}\t\t{}\t\t{}\t\t{}\t\t{}"

def create_model(model_arff, classifier, options, filename):
    print("create_model()")
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



def predict_all(scheduled_data):
    jvm.start(packages=True, max_heap_size="2048m")
    print("weka: predict all")
    print(len(scheduled_data))
    for race_key in scheduled_data:
        # evaluate_predictions("TS_550_B_J48_C0_75.model", scheduled_data[race_key])
        predict("TS_550_B", scheduled_data[race_key])
    jvm.stop()






def predict(race_key, arff_data):
    print("predict")

    # filename = "arff/{}.model".format(race_key)
    filename = "weka_models/TS_550_B_J48_C0_75.model"
    uuid_list = get_uuid_list(arff_data)
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    scheduled_data = loader.load_file(arff_data)
    print(scheduled_data)
    scheduled_data = remove_uuid(scheduled_data)
    print(scheduled_data)
    scheduled_data = nominalize(scheduled_data)
    scheduled_data.class_is_last()
    model = Classifier(jobject=serialization.read(filename))
    make_predictions(model, scheduled_data, uuid_list)
    # try:
    #     model = Classifier(jobject=serialization.read(filename))
    #     make_predictions(model, filtered_scheduled, uuid_list)
    # except:
    #     pass
    # print(arff_data)
    # filename = "weka_models/{}_J48_C0_75.model".format(race_key)
    # uuid_list = get_uuid_list(arff_data)
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    # print(uuid_list)
    # loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    # scheduled_data = loader.load_file(arff_data)
    # print(scheduled_data)
    # scheduled_data = remove_uuid(scheduled_data)
    # print(scheduled_data)
    #
    # scheduled_data = nominalize(scheduled_data)
    # print(scheduled_data)
    #
    # scheduled_data.class_is_last()
    # try:
    #     model = Classifier(jobject=serialization.read(filename))
    #     new_get_predictions(scheduled_data, uuid_list, model)
    #     # make_predictions(model, scheduled_data, uuid_list)
    # except:
    #     pass

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


def evaluate_predictions(model_name, arff_data):
    print("{}:\n".format(model_name)) # WD_548_C_J48_C0_75.model
    uuid_list = get_uuid_list(arff_data)
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    test_data = loader.load_file(arff_data)
    test_data = remove_uuid(test_data)
    test_data = nominalize(test_data)
    test_data.class_is_last()
    model = Classifier(jobject=serialization.read("weka_models/{}".format(model_name)))
    predictions = new_get_predictions(test_data, uuid_list, model)
    
    range_width = .25
    current_range_min = 0
    absolute_max = 8.0
    range_starts = []
    bet_counts = []
    win_winnings = []
    place_winnings = []
    show_winnings = []
    prediction_count = len(predictions)

    while current_range_min < absolute_max:
        current_range_max = current_range_min + range_width
        range_win = 0
        range_place = 0
        range_show = 0
        range_count = 0


        for prediction in predictions:
            participant = prediction["participant"]
            if current_range_min <= prediction["prediction"] <= current_range_max:
                 range_count += 1
                 range_win += get_win_bet_earnings(participant)
                 range_place += get_place_bet_earnings(participant)
                 range_show += get_show_bet_earnings(participant)

        if range_count > 0:
            range_starts.append(current_range_min)
            bet_counts.append(range_count)
            win_winnings.append(range_win/range_count)
            place_winnings.append(range_place/range_count)
            show_winnings.append(range_show/range_count)

        current_range_min += range_width

    if len(bet_counts) > 0:
        print("Prediction Breakdown:\n")
        print("{}\t\t{}\t\t{}\t\t{}\t\t{}".format(
            "Range",
            "Win",
            "Place",
            "Show",
            "Predictions/Race"
        ))
        for each in range_starts:
            index = range_starts.index(each)
            percent = int(100*bet_counts[index]/prediction_count)
            # if percent > 0:
            # print("{}: {}%".format(each, percent))
            bet_count = bet_counts[index]
            print("{}-{}\t\t{}\t\t{}\t\t{}\t\t{}".format(
                round(each, 2),
                round(each + range_width, 2),
                round(win_winnings[index], 2),
                round(place_winnings[index], 2),
                round(show_winnings[index], 2),
                round(float(bet_count*8)/float(prediction_count), 2)
            ))

def dup_evaluate_predictions(model_name, arff_data):
    print("{}:\n".format(model_name)) # WD_548_C_J48_C0_75.model
    uuid_list = get_uuid_list(arff_data)
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    test_data = loader.load_file(arff_data)
    test_data = remove_uuid(test_data)
    test_data = nominalize(test_data)
    test_data.class_is_last()
    model = Classifier(jobject=serialization.read("weka_models/{}".format(model_name)))
    predictions = new_get_predictions(test_data, uuid_list, model)
    print(predictions[0])
    #
    # range_width = .25
    # current_range_min = 0
    # absolute_max = 8.0
    # range_starts = []
    # bet_counts = []
    # win_winnings = []
    # place_winnings = []
    # show_winnings = []
    # prediction_count = len(predictions)
    #
    # while current_range_min < absolute_max:
    #     current_range_max = current_range_min + range_width
    #     range_win = 0
    #     range_place = 0
    #     range_show = 0
    #     range_count = 0
    #
    #
    #     for prediction in predictions:
    #         participant = prediction["participant"]
    #         if current_range_min <= prediction["prediction"] <= current_range_max:
    #              range_count += 1
    #              range_win += get_win_bet_earnings(participant)
    #              range_place += get_place_bet_earnings(participant)
    #              range_show += get_show_bet_earnings(participant)
    #
    #     if range_count > 0:
    #         range_starts.append(current_range_min)
    #         bet_counts.append(range_count)
    #         win_winnings.append(range_win/range_count)
    #         place_winnings.append(range_place/range_count)
    #         show_winnings.append(range_show/range_count)
    #
    #     current_range_min += range_width
    #
    # if len(bet_counts) > 0:
    #     print("Prediction Breakdown:\n")
    #     print("{}\t\t{}\t\t{}\t\t{}\t\t{}".format(
    #         "Range",
    #         "Win",
    #         "Place",
    #         "Show",
    #         "Predictions/Race"
    #     ))
    #     for each in range_starts:
    #         index = range_starts.index(each)
    #         percent = int(100*bet_counts[index]/prediction_count)
    #         # if percent > 0:
    #         # print("{}: {}%".format(each, percent))
    #         bet_count = bet_counts[index]
    #         print("{}-{}\t\t{}\t\t{}\t\t{}\t\t{}".format(
    #             round(each, 2),
    #             round(each + range_width, 2),
    #             round(win_winnings[index], 2),
    #             round(place_winnings[index], 2),
    #             round(show_winnings[index], 2),
    #             round(float(bet_count*8)/float(prediction_count), 2)
    #         ))


def get_win_bet_earnings(participant):
    if participant.final == 1:
        try:
            return participant.straight_wager.win
        except:
            pass
    return 0

def get_place_bet_earnings(participant):
    if participant.final <=2:
        try:
            earnings = participant.straight_wager.place
            if earnings:
                return earnings
        except:
            pass
    return 0

def get_show_bet_earnings(participant):
    if participant.final <= 3:
        try:
            if participant.straight_wager.show:
                return participant.straight_wager.show
            else:
                return 0
        except:
            pass
    return 0


def new_get_predictions(filtered_test, uuid_list, model):
    print("new_get_predictions")
    predictions = []
    for index, inst in enumerate(filtered_test):
        participant = Participant.objects.get(uuid=uuid_list[index])
        prediction = model.classify_instance(inst)
        predictions.append({
            "participant": participant,
            "prediction": prediction})
        # print("{}: {}".format(participant.dog.name, prediction))
    return predictions



def make_predictions(cls, data, uuid_list):
    print('make predictions')
    for index, inst in enumerate(data):
        pred = cls.classify_instance(inst)
        print(pred)
        # save_prediction(
        #     Participant.objects.get(uuid=uuid_list[index]),
        #     pred
        # )

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


def get_uuid_list(filename):
    arff_file = open(filename, "r")
    uuids = []
    for line in arff_file:
        if len(line) > 100:
            uuids.append(line.split(",")[0])
    return uuids
