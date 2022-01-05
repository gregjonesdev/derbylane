from pww.utilities.arff import (
    create_arff,
    get_training_arff,
    get_testing_arff)

from pww.utilities.ultraweka import (
    create_model,
    get_uuid_line_index)

from miner.utilities.common import two_digitizer


table_string = "{}\t\t{}\t\t{}\t\t{}"

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

    print("Profitability of bets (W/P/S) on dogs predicted to finish: {}\n".format(prediction))
    c = 0.15
    c_min = 0.15
    c_max = 0.15
    c = c_min
    while c <= c_max:
        c = round(c, 2)
        print("Confidence factor: {}".format(c))

        print(table_string.format(
        "Cutoff",
        "W",
        "P",
        "S"))
        model = create_model(
            training_arff,
            classifier_name,
            str(c),
            race_key,
            loader)
        evaluate_model_cutoffs(model, prediction)
        print("\n")
        c += 0.05
    return daily_results

def evaluate_model_cutoffs(model, prediction):
    starting_cutoff = 0.7
    ending_cutoff = 1.0
    cutoff_increment = 0.05
    confidence_cutoff = 0.5
    cutoff = starting_cutoff
    while cutoff <= ending_cutoff:
        cutoff = round(cutoff, 2)
        print(table_string.format(
            cutoff,
            "W",
            "P",
            "S"
        ))
        cutoff += cutoff_increment

        # prediction_list = get_prediction_list(
        #     model,
        #     testing_data,
        #     confidence_cutoff)
        # self.print_returns(prediction_list, str(c), race_key, loader, prediction)
