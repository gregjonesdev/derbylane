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
breakdown_string="{}\t\t{}\t\t{}\t\t{}\t\t{}"

classifiers = [
    # "weka.classifiers.functions.SMO",
    # "weka.classifiers.trees.J48",
    "weka.classifiers.rules.ZeroR",
    "weka.classifiers.functions.SMOreg",
    "weka.classifiers.trees.REPTree",
    "weka.clusterers.SimpleKMeans",
    ]


def create_model(model_arff, race_key, classifier, options, filename):
    jvm.start(packages=True, max_heap_size="2048m")
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    unfiltered_data = loader.load_file(model_arff)
    remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "first"])
    remove.inputformat(unfiltered_data)
    filtered_data = remove.filter(unfiltered_data)
    filtered_data.class_is_last()
    cls = Classifier(classname=classifier, options=options)
    cls.build_classifier(filtered_data)
    filename = "test_models/{}_{}.model".format(race_key, filename)
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

def evaluate_predictions(model_name, arff_data):
    print("{}:\n".format(model_name))
    uuid_list = get_uuid_list(arff_data)



    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    test_data = loader.load_file(arff_data)
    remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "first"])
    remove.inputformat(test_data)
    filtered_test = remove.filter(test_data)
    filtered_test.class_is_last()
    model = Classifier(jobject=serialization.read("test_models/{}".format(model_name)))
    predictions = new_get_predictions(filtered_test, uuid_list, model)

    range_width = 2
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
        for each in range_starts:
            index = range_starts.index(each)
            percent = 100*int(bet_counts[index]/prediction_count)
            print("{}: {}%".format(each, percent))



        print("Ideal betting ranges:\n")
        print(breakdown_string.format(
            "Bet",
            "Min",
            "Max",
            "$/bet",
            "Bets"
        ))
        print_bet_breakdown(
            win_winnings,
            range_starts,
            bet_counts,
            prediction_count,
            range_width,
            'Win')
        print_bet_breakdown(
            place_winnings,
            range_starts,
            bet_counts,
            prediction_count,
            range_width,
            'Place')
        print_bet_breakdown(
            show_winnings,
            range_starts,
            bet_counts,
            prediction_count,
            range_width,
            'Show')
    else:
        print("No bets recorded.")
    print("\n\n")

def print_bet_breakdown(
    winnings,
    range_starts,
    bet_counts,
    prediction_count,
    range_width,
    type):
    max_winnings = max(winnings)
    index = winnings.index(max_winnings)
    optimal_range_start = range_starts[index]
    optimal_range_stop = optimal_range_start + range_width
    bet_count = bet_counts[index]
    win_per_bet = float(max_winnings)/float(bet_count)
    bets_per_race = float(bet_count*8)/float(prediction_count)
    # print("{}: {}-{}. (${}/bet)".format(
    #     type,
    #     optimal_range_start,
    #     optimal_range_stop,
    #     round(win_per_bet, 2)))
    print(breakdown_string.format(
        type,
        optimal_range_start,
        optimal_range_stop,
        round(win_per_bet, 2),
        round(bets_per_race, 3)
    ))



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
            return participant.straight_wager.place
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
    predictions = []
    for index, inst in enumerate(filtered_test):
        participant = Participant.objects.get(uuid=uuid_list[index])
        predictions.append({
            "participant": participant,
            "prediction": model.classify_instance(inst)})
    return predictions



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
