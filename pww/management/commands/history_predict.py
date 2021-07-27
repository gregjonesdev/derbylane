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
from pww.utilities.weka import evaluate_all

from miner.utilities.constants import (
    csv_columns,
    focused_distances,
    focused_grades)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--venue', type=str)
        parser.add_argument('--grade', type=str)

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


    def handle(self, *args, **options):
        today = datetime.date.today()
        scheduled_start = "2021-01-01"
        start_datetime = datetime.datetime.strptime(scheduled_start, "%Y-%m-%d")
        start_date = start_datetime.date()
        arff_list = []
        venue_code = sys.argv[3]
        grade_name = sys.argv[5]
        # for venue in Venue.objects.filter(is_focused=True):
        venue_metrics = Metric.objects.filter(
            participant__race__chart__program__venue__code=venue_code)
        for distance in focused_distances[venue_code]:
            print("Distance: {}".format(distance))
            distance_metrics = venue_metrics.filter(
                participant__race__distance=distance,
            )
            print("Grade: {}".format(grade_name))
            graded_metrics = distance_metrics.filter(
                participant__race__grade__name=grade_name,
            )
            if len(graded_metrics) > 0:
                scheduled_metrics = graded_metrics.filter(
                participant__race__chart__program__date__gte=start_date)
                if len(scheduled_metrics) > 0:
                    race_key = "{}_{}_{}".format(venue_code, distance, grade_name)
                    arff_list.append(self.create_arff(
                        "arff/{}.arff".format(race_key),
                        graded_metrics, start_date))
        evaluate_all(arff_list, venue_code, grade_name)
