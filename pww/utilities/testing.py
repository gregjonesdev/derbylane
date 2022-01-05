from pww.utilities.arff import (
    create_arff,
    get_training_arff,
    get_testing_arff)

from pww.utilities.ultraweka import (
    create_model,
    get_uuid_line_index,
    get_prediction_confidence)

from miner.utilities.common import two_digitizer

from rawdat.models import Participant

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
    prediction,
    loader):
    daily_results = {} # uuid: pred

    training_metrics = all_metrics.filter(
        participant__race__chart__program__date__lt=target_date)
    testing_metrics = all_metrics.filter(
        participant__race__chart__program__date=target_date)
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

    print("Profitability of bets (W/P/S) on dogs predicted to finish: {}".format(prediction))
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
        evaluate_model_cutoffs(model, prediction, testing_arff)
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
            print(prediction_table_string.format(
                participant.race.number,
                participant.dog.name[:5],
                prediction,
                round(confidence, 2),
                current_win_return,
                current_place_return,
                current_show_return))

        print(prediction_table_string.format(
            "Average",
            " ",
            " ",
            " ",
            get_average_return(win_returns),
            get_average_return(place_returns),
            get_average_return(show_returns),
            ))

def get_average_return(list):
    if len(list):
        return round(sum(list)/len(list), 2)
    else:
        return "   "


def evaluate_model_cutoffs(model, prediction, testing_arff):
    starting_cutoff = 0.7
    ending_cutoff = 1.0
    cutoff_increment = 0.05
    cutoff = starting_cutoff
    while cutoff <= ending_cutoff:
        cutoff = round(cutoff, 2)
        print("Cutoff: {}\n".format(cutoff))

        prediction_list = get_prediction_confidence(
            testing_arff,
            model,
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
