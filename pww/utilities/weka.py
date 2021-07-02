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
    print(model_name)
    uuid_list = get_uuid_list(arff_data)



    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    test_data = loader.load_file(arff_data)
    remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "first"])
    remove.inputformat(test_data)
    filtered_test = remove.filter(test_data)
    filtered_test.class_is_last()
    model = Classifier(jobject=serialization.read("arff/{}".format(model_name)))
    predictions = new_get_predictions(filtered_test, uuid_list, model)

    cutoff = 0.1
    # successful_bets = 0
    total_bets = 0
    ideal_range_bet_count = 0
    current_min = 0.0
    current_max = 0.1
    ideal_min = current_min
    ideal_max = current_max
    absolute_max = 8.0
    absolute_min = 0.0
    max_winnings = 0
    max_profit_per_bet = 0
    winning_position = 1
    max_profit_scope = 0 # number of bets * profit per bet

    while current_max < absolute_max:
        current_min = absolute_min
        while current_min < current_max:
            current_bet_count = 0
            successful_bets = 0
            winnings = 0

            for prediction in predictions:
                if current_min <= prediction["prediction"] <= current_max:
                    current_bet_count += 1
                    total_bets += 1
                    if prediction["participant"].final <= winning_position:
                        successful_bets += 1
                        try:
                            winnings += prediction["participant"].straight_wager.win
                        except:
                            pass
            if current_bet_count > 0:
                current_profit_per_bet = winnings/current_bet_count
                current_profit_scope = current_bet_count*float(current_profit_per_bet)
                if current_profit_scope > max_profit_scope:
                    max_profit_per_bet = current_profit_per_bet
                    max_profit_scope = current_profit_scope
                    ideal_min = current_min
                    ideal_max = current_max
                    ideal_range_bet_count = current_bet_count

            current_min += 0.1
        current_max +=0.1
    print("Optimal Range: {} - {} at avg return ${}/bet".format(
        round(ideal_min, 3),
        round(ideal_max, 3),
        round(max_profit_per_bet, 2)
    ))
    print("This range represents {}% of all bets.".format(
        round(ideal_range_bet_count/total_bets*100, 1)
    ))





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
