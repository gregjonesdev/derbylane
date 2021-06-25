import csv
import sys

from pathlib import Path

from django.core.management.base import BaseCommand

from pww.models import Metric
from rawdat.models import Venue
from pww.utilities.weka import create_model

from miner.utilities.constants import (
    # valued_grades,
    # chart_times,
    # focused_distances,
    # focused_venues,
    csv_columns,
    )


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--venue', type=str)
        parser.add_argument('--grade', type=str)
        parser.add_argument('--distance', type=int)


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



    def handle(self, *args, **options):
        print("Create model")
        print(sys.argv[3])
        print(sys.argv[5])
        print(sys.argv[7])
        arff_directory = "arff"

        Path(arff_directory).mkdir(
                parents=True,
                exist_ok=True)


        distance = 550

        venue = Venue.objects.get(code='TS')

        grade = 'B'




        arff_data = []
        # for venue in venues:
        #     print(venue)
        metrics = Metric.objects.filter(
            participant__race__chart__program__venue=venue,
            participant__race__distance=distance,
            participant__race__grade__name=grade,
            final__isnull=False)
            # print(len(venue_metrics))
            # for distance in distances:
        # distance_metrics = venue_metrics.filter(
        #     participant__race__distance=distance,
        #     participant__race__grade__name=grade_name,
        # )
                # print("Distance: {} Metrics: {}".format(distance, len(distance_metrics)))
                # for grade_name in grades:
        # graded_metrics = distance_metrics.filter(
        #     participant__race__grade__name=grade_name,
        # )
                    # print("Processing Grade {}. Metrics: {}".format(grade_name, len(graded_metrics)))
                    # completed_metrics = graded_metrics.filter(final__isnull=False)
                    # scheduled_metrics = graded_metrics.filter(
                    #     final__isnull=True,
                    #     participant__race__chart__program__date=today)
        print(len(metrics))
        raise SystemExit(0)
        race_key = "{}_{}_{}".format(venue.code, distance, grade_name)
        # if len(scheduled_metrics) > 0:
            # scheduled_filename = "arff/{}_scheduled.arff".format(race_key)
        model_filename = "arff/{}_model.arff".format(race_key)
        arff_data.append({
            # "scheduled": self.create_arff(
            #     scheduled_filename,
            #     scheduled_metrics,
            #     False),
            "results": self.create_arff(
                results_filename,
                completed_metrics,
                False),
        #                     "nominal": self.create_arff(
        #                         results_filename,
        #                         completed_metrics,
        #                         True),
                        })
        create_model(arff_data)
