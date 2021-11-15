from miner.utilities.constants import csv_columns

def write_headers(arff_file, is_nominal):
    for each in csv_columns:
        if is_nominal and each == "Fi":
            arff_file.write("@attribute {} nominal\n".format(each))
        elif each == "PID":
            arff_file.write("@attribute PID string\n")
        elif each == "Se":
            arff_file.write("@attribute Se {M, F}\n")
        else:
            arff_file.write("@attribute {} numeric\n".format(each))
    arff_file.write("@data\n")
    return arff_file


def create_arff(filename, metrics, is_nominal, is_training):

    arff_file = open(filename, "w")
    arff_file.write("@relation Metric\n")
    arff_file = write_headers(arff_file, is_nominal)
    for metric in metrics:
        csv_metric = metric.build_csv_metric(is_training)
        if csv_metric:
            arff_file.writelines(csv_metric)
    return filename
