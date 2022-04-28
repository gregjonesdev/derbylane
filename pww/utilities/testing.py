from pww.utilities.arff import (
    get_training_arff,
    get_testing_arff)

from pww.utilities.ultraweka import (
    create_model,
    get_uuid_line_index,
    get_prediction_confidence)

from miner.utilities.common import two_digitizer

from rawdat.models import Participant
from pww.models import Metric

from pww.utilities.ultraweka import get_metrics


table_string = "{}\t\t{}\t\t{}\t\t{}"

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

def get_daily_results(
    classifier_name,
    race_key,
    target_date,
    all_metrics,
    target_prediction,
    loader):
    daily_results = {} # uuid: pred

    # training_metrics = all_metrics.filter(
    #     participant__race__chart__program__date__range=("2017-01-01", target_date))
    training_metrics = Metric.objects.filter(
        participant__race__chart__program__venue__code="TS",
        # participant__race__distance=distance,
        # participant__race__grade__name=grade_name,
        participant__race__chart__program__date__gte="2018-01-01")



    print(len(training_metrics))
    testing_metrics = all_metrics.filter(
        participant__race__chart__program__date__range=("2021-12-04", "2022-01-04"))
    print(len(testing_metrics))
    is_nominal = False
    training_arff = get_training_arff(
        race_key,
        training_metrics,
        is_nominal)
    testing_arff = get_testing_arff(
        race_key,
        testing_metrics,
        is_nominal)
    uuid_line_index = get_uuid_line_index(testing_arff)

    print("Profitability of bets (W/P/S) on dogs predicted to finish: {}".format(target_prediction))
    c = 0.15
    c_min = 0.15
    c_max = 0.5
    c = c_min
    while c <= c_max:
        c = round(c, 2)
        print("Model C Factor: {}\n".format(c))
        model = create_model(
            training_arff,
            classifier_name,
            str(c),
            race_key,
            loader)
        evaluate_model_cutoffs(model, target_prediction, testing_arff)
        print("\n")
        c += 0.05
    return daily_results

def get_win_profitability(cutoff, ):
    return "W"


def print_prediction_table(prediction_list):
    prediction_table_string = "{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}"
    if len(prediction_list) > 0:
        print(prediction_table_string.format(
            "Race",
            "Dog",
            "Pred.",
            "Conf.",
            "W",
            "P",
            "S"))
        win_returns = []
        place_returns = []
        show_returns = []
        for uuid in prediction_list:
            participant = Participant.objects.get(uuid=uuid)
            current_win_return = get_win_return(participant)
            current_place_return = get_place_return(participant)
            current_show_return = get_show_return(participant)
            win_returns.append(current_win_return)
            place_returns.append(current_place_return)
            show_returns.append(current_show_return)
            prediction_tuple = prediction_list[uuid]
            prediction = prediction_tuple[0]
            confidence = prediction_tuple[1]
            # print(prediction_table_string.format(
            #     participant.race.number,
            #     participant.dog.name[:5],
            #     prediction,
            #     round(confidence, 2),
            #     current_win_return,
            #     current_place_return,
            #     current_show_return))

        print(prediction_table_string.format(
            "Average",
            " ",
            " ",
            " ",
            get_return_and_count(win_returns),
            get_return_and_count(place_returns),
            get_return_and_count(show_returns),
            ))

def get_average_return(list):
    if len(list):
        return round(sum(list)/len(list), 2)
    else:
        return "   "

def get_count(list):
    count = 0
    for item in list:
        if int(item) > 0:
            count += 1
    return "1:{}".format(round((len(list)/count), 2))

def get_return_and_count(list):
    avg_return = get_average_return(list)
    count = get_count(list)
    return "{} ({})".format(avg_return, count)

def evaluate_model_cutoffs(model, target_prediction, testing_arff):
    starting_cutoff = 0.5
    ending_cutoff = 1.0
    cutoff_increment = 0.05
    cutoff = starting_cutoff
    while cutoff <= ending_cutoff:
        cutoff = round(cutoff, 2)
        print("Cutoff: {}\n".format(cutoff))

        prediction_list = get_prediction_confidence(
            testing_arff,
            model,
            target_prediction,
            cutoff)
        # print(prediction_list)
        print_prediction_table(prediction_list)
        print("\n")
        # print(table_string.format(
        #     cutoff,
        #     get_win_profitability(cutoff, ),
        #     "P",
        #     "S"
        # ))
        cutoff += cutoff_increment

        # self.print_returns(prediction_list, str(c), race_key, loader, prediction)
