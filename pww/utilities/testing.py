def get_daily_results(target_date, all_metrics, loader):
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

    c = 0.27
    confidence_cutoff = 0.5
    model_name = create_model(
        training_arff,
        classifier_name,
        str(c),
        race_key,
        loader)
    model = Classifier(jobject=serialization.read(model_name))
    prediction_list = get_prediction_list(
        model,
        testing_data,
        uuid_line_index,
        confidence_cutoff)
    # self.print_returns(prediction_list, str(c), race_key, loader, prediction)

    return daily_results
