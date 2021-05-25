import csv
import datetime

from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from pww.models import Prediction, Metric
from rawdat.models import Race, Venue
from pww.utilities.weka import make_predictions

from miner.utilities.constants import (
    valued_grades,
    chart_times,
    venue_distances,
    csv_columns,
    )


class Command(BaseCommand):


    def create_csv(self, filename, metrics):
        arff_file = open(filename, "w")
        arff_file.write("@relation Metric\n")

        for each in csv_columns:
            if each == "PID":
                arff_file.write("@attribute PID string\n")
                # csv_writer.writerow(["@attribute PID string"])
            elif each == "Se":
                arff_file.write("@attribute Se {M, F}\n")
                # csv_writer.writerow(["@attribute Se {M, F}"])
            else:
                # csv_writer.writerow(["@attribute {} numeric".format(each)])
                arff_file.write("@attribute {} numeric\n".format(each))

        # with open(filename, 'w', newline='') as write_obj:
        #     csv_writer = csv.writer(write_obj)
        #
        #     csv_writer.writerow(["@relation Metrics"])
        #     # csv_writer.writerow(["\n"])
        #
        #     for each in csv_columns:
        #         if each == "PID":
        #             csv_writer.writerow(["@attribute PID string"])
        #         elif each == "Se":
        #             csv_writer.writerow(["@attribute Se {M, F}"])
        #         else:
        #             csv_writer.writerow(["@attribute {} numeric".format(each)])
        #
        #     # csv_writer.writerow(["\n"])
        #
        #
        #     csv_writer.writerow(["@data"])
        #
        arff_file.write("@data\n")

        for metric in metrics:
            arff_file.writelines(metric.build_csv_metric())


    def handle(self, *args, **options):
        csv_directory = "csv"
        Path(csv_directory).mkdir(
                parents=True,
                exist_ok=True)
        today = datetime.date.today()
        for venue in Venue.objects.filter(is_active=True):
            venue_metrics = Metric.objects.filter(
                participant__race__chart__program__venue=venue)
            for distance in venue_distances[venue.code]:
                distance_metrics = venue_metrics.filter(
                    participant__race__distance=distance,
                )
                for grade_name in valued_grades:
                    graded_metrics = distance_metrics.filter(
                        participant__race__grade__name=grade_name,
                    )
                    completed_metrics = graded_metrics.filter(final__isnull=False)
                    scheduled_metrics = graded_metrics.filter(final__isnull=True)
                    race_key = "{}_{}_{}".format(venue.code, distance, grade_name)
                    if len(scheduled_metrics) > 0:
                        scheduled_filename = "csv/{}_scheduled.arff".format(race_key)
                        scheduled_csv = self.create_csv(
                            scheduled_filename,
                            scheduled_metrics)
                        results_filename = "csv/{}_results.arff".format(race_key)

                        results_csv = self.create_csv(
                            results_filename,
                            completed_metrics)
                        make_predictions(scheduled_filename, results_filename)
