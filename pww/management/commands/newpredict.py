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
from pww.utilities.weka import predict_all

from miner.utilities.constants import (
    csv_columns,
    focused_distances,
    focused_grades)


class Command(BaseCommand):

    def create_arff(self, filename, metrics, start_date):
        arff_file = open(filename, "w")
        arff_file.write("@relation Metric\n")

        arff_file = self.write_headers(arff_file)

        for metric in metrics:
            csv_metric = metric.build_csv_metric(start_date)
            if csv_metric:
                arff_file.writelines(csv_metric)

        return filename


    def write_headers(self, arff_file):
        for each in csv_columns:
            if each == "PID":
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
        today = datetime.date.today()
        scheduled_start = today
        scheduled_start = "2019-01-01"
        start_datetime = datetime.datetime.strptime(scheduled_start, "%Y-%m-%d")
        start_date = start_datetime.date()
        arff_files = []
        for venue in Venue.objects.filter(is_focused=True):
            # print(venue)
            venue_code = venue.code
            venue_metrics = Metric.objects.filter(
                participant__race__chart__program__venue=venue)
            for distance in focused_distances[venue_code]:
                # print("Distance: {}".format(distance))
                distance_metrics = venue_metrics.filter(
                    participant__race__distance=distance,
                )
                for grade_name in focused_grades[venue_code]:
                    # print("Grade: {}".format(grade_name))
                    graded_metrics = distance_metrics.filter(
                        participant__race__grade__name=grade_name,
                    )
                    if len(graded_metrics) > 0:
                        # print(len(graded_metrics))
                        scheduled_metrics = graded_metrics.filter(
                        participant__race__chart__program__date__gte=scheduled_start)
                        if len(scheduled_metrics) > 0:
                            # print(len(scheduled_metrics))
                            training_metrics = graded_metrics.filter(
                                participant__race__chart__program__date__lt=scheduled_start)
                            # print(len(training_metrics))
                            race_key = "{}_{}_{}".format(venue_code, distance, grade_name)
                            arff_files.append(self.create_arff(
                                "arff/{}.arff".format(race_key),
                                graded_metrics, start_date))
        predict_all(arff_files)
