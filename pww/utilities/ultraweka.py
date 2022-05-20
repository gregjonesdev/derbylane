from miner.utilities.constants import csv_columns
from pww.utilities.classifiers import classifiers
from weka.attribute_selection import ASSearch
from weka.attribute_selection import ASEvaluation
from weka.attribute_selection import AttributeSelection
from weka.classifiers import Classifier
from weka.filters import Filter
from rawdat.models import Participant
import weka.core.serialization as serialization
from weka.core.converters import Loader
from django.core.exceptions import ObjectDoesNotExist
from pww.models import Prediction

def get_filename(model_directory, model_name):
    return "{}/{}.model".format(model_directory, model_name)

def nominalize(data):
    nominalize = Filter(
        classname="weka.filters.unsupervised.attribute.NumericToNominal",
        options=["-R", "{}".format(csv_columns.index('Fi'))])
    nominalize.inputformat(data)
    return nominalize.filter(data)

def get_attr_classifier(base_classifier):
    attr_classifier = Classifier(
        classname="weka.classifiers.meta.AttributeSelectedClassifier")
    search = ASSearch(
        classname="weka.attributeSelection.BestFirst",
        options=["-D", "1", "-N", "3"])
    evaluator = ASEvaluation(
        classname="weka.attributeSelection.CfsSubsetEval",
        options=["-P", "1", "-E", "1"])
    attr_classifier.set_property("classifier", base_classifier.jobject)
    attr_classifier.set_property("evaluator", evaluator.jobject)
    attr_classifier.set_property("search", search.jobject)
    return attr_classifier

def get_filtered_data(loaded_data, is_nominal):
    filtered_data = remove_uuid(loaded_data)
    filtered_data.class_is_last()
    if is_nominal:
        return nominalize(filtered_data)
    return filtered_data

def get_model(model_directory, model_name):
    filename = get_filename(model_directory, model_name)
    return Classifier(jobject=serialization.read(filename))

def save_model(training_arff, classifier_name, model_directory, model_name):
    classifier_attributes = classifiers[classifier_name]
    filename = get_filename(model_directory, model_name)
    loader = Loader(classname="weka.core.converters.ArffLoader")
    loaded_data = loader.load_file(training_arff)
    filtered_data = get_filtered_data(
        loaded_data,
        classifier_attributes["is_nominal"])
    base_classifier = Classifier(
        classname=classifier_attributes["path"],
        options=classifier_attributes["options"])
    attr_classifier = get_attr_classifier(base_classifier)
    attr_classifier.build_classifier(filtered_data)
    serialization.write(filename, attr_classifier)

def get_model_name(venue_code, grade_name, start_date):
    return "{}_{}_{}".format(
        venue_code,
        grade_name,
        start_date.replace("-", "_"))

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

def format_distribution(dist):
    formatted_dist = []
    for each in dist:
        formatted_dist.append(round(each, 1))
    return formatted_dist

def evaluate_confidence(classifier, filtered_data, uuid_line_index):
    for index, inst in enumerate(filtered_data):
        if index in uuid_line_index.keys():
            uuid = uuid_line_index[index]
            prediction = classifier.classify_instance(inst)
            dist = classifier.distribution_for_instance(inst)
            print("{}: {} {}".format(
                uuid,
                prediction,
                format_distribution(dist)))

def build_interval_object(start, stop, interval):
    interval_object = {}
    current_low = start
    while current_low + interval <= stop:
        interval_object["{}".format(current_low)] = []
        current_low += interval
    return interval_object


def get_average_win(list):
    if len(list) < 1:
        return "-"
    bet_returns = []
    for each in list:
        participant = Participant.objects.get(uuid=each["uuid"])
        bet_returns.append(get_win_return(participant))
    # print("Win:")

    winner = 0
    for each in bet_returns:
        if each > 2:
            winner +=1
    # print(round(100*winner/len(bet_returns), 2))
    # print(bet_returns)
    return round(sum(bet_returns)/len(bet_returns), 2)

def get_average_place(list):
    if len(list) < 1:
        return "-"
    bet_returns = []
    for each in list:
        participant = Participant.objects.get(uuid=each["uuid"])
        bet_returns.append(get_place_return(participant))
    # print("Place:")

    winner = 0
    for each in bet_returns:
        if each > 2:
            winner +=1
    # print(round(100*winner/len(bet_returns), 2))
    # print(bet_returns)
    return round(sum(bet_returns)/len(bet_returns), 2)

def get_average_show(list):
    if len(list) < 1:
        return "-"
    bet_returns = []
    for each in list:
        participant = Participant.objects.get(uuid=each["uuid"])
        bet_returns.append(get_show_return(participant))
    return round(sum(bet_returns)/len(bet_returns), 2)

def get_win_return(participant):
    try:
        return float(participant.straight_wager.win)
    except:
        return 0

def get_place_return(participant):
    try:
        return float(participant.straight_wager.place)
    except:
        return 0

def get_show_return(participant):
    try:
        return float(participant.straight_wager.show)
    except:
        return 0

def get_profit_potential(percent, payout):
    try:
        if payout <= 2.0:
            return "-----------"
        return "{} [{}]".format(payout, round(payout*percent,2))
    except TypeError:
        return ""


def evaluate_numeric_exotic(classifier, filtered_data, uuid_line_index):
    prediction_numbers = [0, 0, 0]
    optimal_trifecta = {
        "scenario": "",
        "average_return": 0,
        "potential": 0,
        "success_rate": 0,
    }




    start = 1
    stop = 8
    interval = .0625
    count = 0
    while prediction_numbers[0] < stop:
        print("Evaluating {}-{}-{}".format(
            "{}-{}".format(numbers[0], numbers[0]+interval),
            "{}-{}".format(numbers[1], numbers[1]+interval),
            "{}-{}".format(numbers[2], numbers[2]+interval)))
        prediction_numbers[0] += interval
    # interval_object = build_interval_object(start, stop, interval)
    # for index, inst in enumerate(filtered_data):
    #     if index in uuid_line_index.keys():
    #         uuid = uuid_line_index[index]
    #         count +=1
    #         prediction = classifier.classify_instance(inst)
    #         for each in interval_object.keys():
    #             key_value = float(each)
    #             if key_value <= prediction < (key_value + interval):
    #                 interval_object[each].append({
    #                     "uuid": uuid,
    #                     "prediction": prediction
    #                 })
    #
    # print("{}\t\t{}\t\t\t{}\t\t{}\t\t{}".format("Range", "Freq", "Win", "Place", "Show"))
    # for each in interval_object.keys():
    #     string_row = "{} - {}\t{} ({}%)\t\t{}\t{}\t{}"
    #     if count > 0:
    #         percent = round((100*len(interval_object[each])/count), 2)
    #     else:
    #         percent = 0
    #     print(string_row.format(
    #         round(float(each), 2),
    #         round(float(each) + interval, 2),
    #         len(interval_object[each]),
    #         percent,
    #         get_profit_potential(percent, get_average_win(interval_object[each])),
    #         get_profit_potential(percent, get_average_place(interval_object[each])),
    #         get_profit_potential(percent, get_average_show(interval_object[each]))))


def evaluate_numeric(classifier, filtered_data, uuid_line_index):
    start = 1
    stop = 8
    interval = .0625
    count = 0
    interval_object = build_interval_object(start, stop, interval)
    for index, inst in enumerate(filtered_data):
        if index in uuid_line_index.keys():
            uuid = uuid_line_index[index]
            count +=1
            prediction = classifier.classify_instance(inst)
            for each in interval_object.keys():
                key_value = float(each)
                if key_value <= prediction < (key_value + interval):
                    interval_object[each].append({
                        "uuid": uuid,
                        "prediction": prediction
                    })

    print("{}\t\t{}\t\t\t{}\t\t{}\t\t{}".format("Range", "Freq", "Win", "Place", "Show"))
    for each in interval_object.keys():
        string_row = "{} - {}\t{} ({}%)\t\t{}\t{}\t{}"
        if count > 0:
            percent = round((100*len(interval_object[each])/count), 2)
        else:
            percent = 0
        # if len(interval_object[each]) > 99:
        #     string_row = "{} - {}:\t{} ({}%)\t{}\t{}\t{}"
        print(string_row.format(
            round(float(each), 2),
            round(float(each) + interval, 2),
            len(interval_object[each]),
            percent,
            get_profit_potential(percent, get_average_win(interval_object[each])),
            get_profit_potential(percent, get_average_place(interval_object[each])),
            get_profit_potential(percent, get_average_show(interval_object[each]))))


        # print(round(float(each), 2))
        # get_average_win(interval_object[each])

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

def save_predictions(prediction_object):
    for uuid in prediction_object.keys():
        participant = Participant.objects.get(uuid=uuid)
        prediction = get_prediction(participant)
        prediction_bet = ""
        if prediction_object[uuid]["W"]:
            prediction_bet += "W"
        if prediction_object[uuid]["P"]:
            prediction_bet += "P"
        if prediction_object[uuid]["S"]:
            prediction_bet += "S"
        prediction.bet = prediction_bet
        prediction.save()


def make_predictions(model, testing_arff, classifier_name, is_nominal, bet_guides):
    uuid_line_index = get_uuid_line_index(testing_arff)
    loader = Loader(classname="weka.core.converters.ArffLoader")
    loaded_data = loader.load_file(testing_arff)
    filtered_data = get_filtered_data(loaded_data, is_nominal)
    prediction_object = {}
    for index, inst in enumerate(filtered_data):
        if index in uuid_line_index.keys():
            uuid = uuid_line_index[index]
            prediction = model.classify_instance(inst)
            for guide in bet_guides:
                if guide["start"] <=prediction < guide["end"]:
                    if not uuid in prediction_object.keys():
                        prediction_object[uuid] = {
                            "W": False,
                            "P": False,
                            "S": False}
                    for char in guide["bet"]:
                        prediction_object[uuid][char] = True;
    save_predictions(prediction_object)


def evaluate_predictions(testing_arff, model, classifier_name):

    classifier_attributes = classifiers[classifier_name]
    is_nominal = classifier_attributes["is_nominal"]
    uuid_line_index = get_uuid_line_index(testing_arff)
    loader = Loader(classname="weka.core.converters.ArffLoader")
    loaded_data = loader.load_file(testing_arff)
    filtered_data = get_filtered_data(loaded_data, is_nominal)
    if is_nominal:
        evaluate_confidence(model, filtered_data, uuid_line_index)
    else:
        evaluate_numeric(model, filtered_data, uuid_line_index)


def evaluate_exotics(testing_arff, model, classifier_name):

    classifier_attributes = classifiers[classifier_name]
    is_nominal = classifier_attributes["is_nominal"]
    uuid_line_index = get_uuid_line_index(testing_arff)
    loader = Loader(classname="weka.core.converters.ArffLoader")
    loaded_data = loader.load_file(testing_arff)
    filtered_data = get_filtered_data(loaded_data, is_nominal)
    if is_nominal:
        print("uh...should there be something here?")
    else:
        evaluate_numeric_exotic(model, filtered_data, uuid_line_index)
