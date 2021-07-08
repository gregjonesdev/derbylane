import csv
import datetime

from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from pww.models import Prediction, Metric
from rawdat.models import Race, Venue
from pww.utilities.weka import predict_all, evaluate_predictions

from miner.utilities.constants import (
    focused_grades,
    focused_distances,
    csv_columns)


class Command(BaseCommand):


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
            elif each == "Se":
                arff_file.write("@attribute Se {M, F}\n")
            else:
                arff_file.write("@attribute {} numeric\n".format(each))

        arff_file.write("@data\n")
        return arff_file



    def handle(self, *args, **options):
        today = datetime.date.today()
        scheduled_data = {}
        for venue in Venue.objects.filter(is_focused=True):
            print(venue)
            venue_code = venue.code
            venue_metrics = Metric.objects.filter(
                participant__race__chart__program__venue=venue)
            for distance in focused_distances[venue_code]:
                print("Distance: {}".format(distance))
                distance_metrics = venue_metrics.filter(
                    participant__race__distance=distance,
                )
                for grade_name in focused_grades[venue_code]:
                    print("Grade: {}".format(grade_name))
                    graded_metrics = distance_metrics.filter(
                        participant__race__grade__name=grade_name,
                    )
                    scheduled_metrics = graded_metrics.filter(
                        participant__race__chart__program__date__gte=today)

                    # print("Metrics Found: {}".format(len(scheduled_metrics)))
                    if len(scheduled_metrics) > 0:
                        race_key = "{}_{}_{}".format(venue.code, distance, grade_name)
                    #     race_key = "SL_583_C"
                        scheduled_filename = "arff/{}_scheduled.arff".format(race_key)
                        scheduled_data[race_key] = self.create_arff(
                            scheduled_filename,
                            scheduled_metrics,
                            False)
        for each in scheduled_data:
            print(scheduled_data[each])
            fake_model = "WD_548_C_J48_C0_75.model"
            evaluate_predictions(fake_model, scheduled_data[each] )
        # predict_all(scheduled_data)
