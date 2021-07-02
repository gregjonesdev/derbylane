# import csv
import sys
import os
import fnmatch
from pathlib import Path

from django.core.management.base import BaseCommand

from pww.models import Metric
from rawdat.models import Venue
# from pww.utilities.weka import create_model

from miner.utilities.constants import (
    # valued_grades,
    # chart_times,
    # focused_distances,
    # focused_venues,
    csv_columns,
    )


class Command(BaseCommand):

    # def add_arguments(self, parser):
    #     parser.add_argument('--model', type=str)

    def create_arff(self, filename, metrics, is_nominal):
        arff_file = open(filename, "w")
        arff_file.write("@relation Metric\n")

        arff_file = self.write_headers(arff_file, is_nominal)

        for metric in metrics:
            csv_metric = metric.build_csv_metric()
            if csv_metric:
                arff_file.writelines(csv_metric)

        return filename


    def write_headers(self, arff_file, is_nominal):
        for each in csv_columns:
            if is_nominal and each == "Fi":
                arff_file.write("@attribute {} nominal\n".format(each))
            elif each == "PID":
                arff_file.write("@attribute PID string\n")
                # csv_writer.writerow(["@attribute PID string"])
            elif each == "Se":
                arff_file.write("@attribute Se {M, F}\n")
                # csv_writer.writerow(["@attribute Se {M, F}"])
            else:
                # csv_writer.writerow(["@attribute {} numeric".format(each)])
                arff_file.write("@attribute {} numeric\n".format(each))

        arff_file.write("@data\n")
        return arff_file


    def get_metrics(self, venue_code, distance, grade_name):
        return Metric.objects.filter(
            participant__race__chart__program__venue__code=venue_code,
            participant__race__distance=distance,
            participant__race__grade__name=grade_name,
            final__isnull=False)

    def get_metrics_to_test(self, models):
        metrics_to_test = {}
        for model in models:
            if "AA" in model.upper():
                race_key = model[:9]
            else:
                race_key = model[:8]
            print(race_key)
            if not race_key in metrics_to_test.keys():
                metrics_to_test[race_key] = []
            metrics_to_test[race_key].append(model)
        return metrics_to_test    


    def handle(self, *args, **options):
        directory = "arff"

        venue_code = 'TS'
        distance = 550
        grade_name = 'A'


        print(self.get_metrics_to_test(
            fnmatch.filter(os.listdir('arff'), '*.model')))
        raise SystemExit(0)
        metrics = self.get_metrics(venue_code, distance, grade_name)


            # metrics_obj = {
            #     "venue_code": model[:2],
            #     "distance": int(model[3:6]),
            #     "grade": model[7:9].replace(".", "")

            # build scheduled arff
            # weka > evaluate_predictions(model, data, uuid_list)
        #
        # print(len(metrics))
        # race_key = "{}_{}_{}".format(venue_code, distance, grade_name)
        # print(race_key)
        # model_filename = "{}/{}_model.arff".format(arff_directory, race_key)
        # print(model_filename)
        # is_nominal = False
        # arff_file = self.create_arff(
        #     model_filename,
        #     metrics,
        #     is_nominal)
        # create_model(arff_file, race_key)
