from miner.utilities.constants import csv_columns
from miner.utilities.urls import arff_directory

def write_headers(arff_file):
    for each in csv_columns:
        if each == "PID":
            arff_file.write("@attribute PID string\n")
        elif each == "Se":
            arff_file.write("@attribute Se {M, F}\n")
        else:
            arff_file.write("@attribute {} numeric\n".format(each))
    arff_file.write("@data\n")
    return arff_file


def create_arff(metrics, is_training):
    if is_training:
        filename = get_arff_filename("train")
    else:
        filename = get_arff_filename("test")
    arff_file = open(filename, "w")
    arff_file.write("@relation Metric\n")
    arff_file = write_headers(arff_file)
    for metric in metrics:
        csv_metric = metric.build_csv_metric(is_training)
        if csv_metric:
            arff_file.writelines(csv_metric)
    return filename


def get_arff_filename(type):
    return "{}/{}.arff".format(
        arff_directory,
        type)


def get_training_arff(metrics):
    is_training = True
    return create_arff(metrics, is_training)

def get_prediction_arff(metrics):
    is_training = False
    return create_arff(metrics, is_training)
