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


    def create_arff(self, filename, metrics):
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

        arff_file.write("@data\n")

        for metric in metrics:
            csv_metric = metric.build_csv_metric()
            if csv_metric:
                arff_file.writelines(csv_metric)

        return filename


    def handle(self, *args, **options):
        arff_directory = "arff"

        Path(arff_directory).mkdir(
                parents=True,
                exist_ok=True)
        today = datetime.date.today()
        arff_data = []
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
                        scheduled_filename = "arff/{}_scheduled.arff".format(race_key)
                        results_filename = "arff/{}_results.arff".format(race_key)
                        arff_data.append({
                            "scheduled": self.create_arff(
                                scheduled_filename,
                                scheduled_metrics),
                            "results": self.create_arff(
                                results_filename,
                                completed_metrics),
                        })
        make_predictions(arff_data)
