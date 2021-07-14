# import csv
import sys
import os
import fnmatch
from pathlib import Path
import weka.core.jvm as jvm
import datetime

from django.core.management.base import BaseCommand

from pww.models import Metric
from rawdat.models import Venue
from pww.utilities.newweka import compare_predictions

from miner.utilities.constants import csv_columns


class Command(BaseCommand):

    def create_arff_file(self, metrics, filename, start_date):
        arff_file = open(filename, "w")
        arff_file.write("@relation Metric\n")
        is_nominal = False
        arff_file = self.write_headers(arff_file, is_nominal)

        for metric in metrics:
            csv_metric = metric.build_csv_metric(start_date)
            if csv_metric:
                arff_file.writelines(csv_metric)

        return filename


    def write_headers(self, arff_file, is_nominal):
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


    def get_metrics(self, venue_code, distance, grade_name):
        return Metric.objects.filter(
            participant__race__chart__program__venue__code=venue_code,
            participant__race__distance=distance,
            participant__race__grade__name=grade_name,
            participant__race__chart__program__date__gte="2019-01-01",
            final__isnull=False)

    def get_race_keys_to_test(self, models):
        race_keys_to_test = {}
        for model in models:
            if "AA" in model.upper():
                race_key = model[:9]
            else:
                race_key = model[:8]
            if not race_key in race_keys_to_test.keys():
                race_keys_to_test[race_key] = []
            race_keys_to_test[race_key].append(model)
        return race_keys_to_test


    def handle(self, *args, **options):
        print("compare")
        distance = 583
        grade_name = "C"
        venue_code = "SL"
        metrics = self.get_metrics(venue_code, distance, grade_name)
        print(len(metrics))
        scheduled_start = "2019-01-01"
        start_datetime = datetime.datetime.strptime(scheduled_start, "%Y-%m-%d")
        start_date = start_datetime.date()
        arff_file = self.create_arff_file(metrics, "metrics.arff", start_date)
        compare_predictions(arff_file)
