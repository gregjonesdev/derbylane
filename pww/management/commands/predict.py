# import csv
import sys
import os
import fnmatch
from pathlib import Path
import weka.core.jvm as jvm
import datetime

from django.core.management.base import BaseCommand

from pww.models import Metric
from rawdat.models import Participant
from pww.utilities.weka import predict_all

from miner.utilities.constants import (
    csv_columns,
    focused_distances,
    focused_grades)


prediction_models = {
    "WD_548_B": "WD_548_B_smo_104.model",
    "WD_548_C": "WD_548_C_smo_008.model",
    "TS_550_B": "TS_550_B_smo_051.model",
    "TS_550_C": "TS_550_C_smo_053.model",
    "SL_583_C": "SL_583_C_smo_025.model",

}


betting_venues = ["WD", "TS", "SL"]

betting_distances = {
    "WD": 548,
    "TS": 550,
    "SL": 583
}

betting_grades = {
    "WD": ["B", "C"],
    "TS": ["B", "C"],
    "SL": ["C"],
}

class Command(BaseCommand):

    def assign_predictions(self, participants, model_name, race_key):
        print("For race_key {} use model {}".format(race_key, model_name))

        # build training arff
        # build testing arff



    def handle(self, *args, **options):
        today = datetime.date.today()
        for venue_code in betting_venues:
            distance = betting_distances[venue_code]
            for grade_name in betting_grades[venue_code]:
                race_key = "{}_{}_{}".format(venue_code, distance, grade_name)
                model_name = prediction_models[race_key]


                participants = Participant.objects.filter(
                    race__distance=distance,
                    race__grade__name=grade_name,
                    race__chart__program__venue__code=venue_code,
                    race__chart__program__date=today
                )
                if len(participants) > 0 :
                    self.assign_predictions(
                        participants,
                        model_name,
                        race_key)


    # def create_arff(self, filename, metrics, start_date):
    #     arff_file = open(filename, "w")
    #     arff_file.write("@relation Metric\n")
    #
    #     arff_file = self.write_headers(arff_file)
    #
    #     for metric in metrics:
    #         csv_metric = metric.build_csv_metric(start_date)
    #         if csv_metric:
    #             arff_file.writelines(csv_metric)
    #
    #     return filename
    #
    #
    # def write_headers(self, arff_file):
    #     for each in csv_columns:
    #         if each == "PID":
    #             arff_file.write("@attribute PID string\n")
    #         elif each == "Se":
    #             arff_file.write("@attribute Se {M, F}\n")
    #         else:
    #             arff_file.write("@attribute {} numeric\n".format(each))
    #
    #     arff_file.write("@data\n")
    #     return arff_file
    #
    #
    # def handle(self, *args, **options):
    #     today = datetime.date.today()
    #     yesterday = today - datetime.timedelta(days=1)
    #     arff_list = []
    #     for venue in Venue.objects.filter(is_focused=True):
    #         print("Building metrics for {}".format(venue))
    #         venue_code = venue.code
    #         venue_metrics = Metric.objects.filter(
    #             participant__race__chart__program__venue=venue)
    #         for distance in focused_distances[venue_code]:
    #             print("Distance: {}".format(distance))
    #             distance_metrics = venue_metrics.filter(
    #                 participant__race__distance=distance,
    #             )
    #             for grade_name in focused_grades[venue_code]:
    #                 print("Grade: {}".format(grade_name))
    #                 graded_metrics = distance_metrics.filter(
    #                     participant__race__grade__name=grade_name,
    #                     participant__race__chart__program__date=yesterday
    #                 )
    #                 if len(graded_metrics) > 0:
    #                     scheduled_metrics = graded_metrics.filter(
    #                     participant__race__chart__program__date__gte=yesterday)
    #                     if len(scheduled_metrics) > 0:
    #                         race_key = "{}_{}_{}".format(venue_code, distance, grade_name)
    #                         arff_list.append(self.create_arff(
    #                             "arff/{}.arff".format(race_key),
    #                             graded_metrics, today))
    #
    #     predict_all(arff_list)
