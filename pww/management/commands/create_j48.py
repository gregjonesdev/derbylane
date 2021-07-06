import csv
import sys
import weka.core.jvm as jvm

from pathlib import Path

from django.core.management.base import BaseCommand

from pww.models import Metric
from rawdat.models import Venue
from pww.utilities.weka import create_model

from miner.utilities.constants import (
    # valued_grades,
    # chart_times,
    focused_distances,
    focused_grades,
    # focused_venues,
    csv_columns,
    )


class Command(BaseCommand):

    def add_arguments(self, parser):
        # parser.add_argument('--venue', type=str)
        # parser.add_argument('--grade', type=str)
        # parser.add_argument('--distance', type=int)
        parser.add_argument('--c', type=float)


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
        # venue_code = sys.argv[3]
        # grade_name = sys.argv[5]
        # distance = sys.argv[7]
        complexity = sys.argv[3]
        arff_directory = "arff"

        Path(arff_directory).mkdir(
                parents=True,
                exist_ok=True)
        jvm.start(packages=True, max_heap_size="2048m")

        for venue in Venue.objects.filter(is_focused=True):
            venue_code = venue.code
            if not venue_code == "CA":
                for distance in focused_distances[venue_code]:
                    for grade_name in focused_grades[venue_code]:
                        print("{}_{}_{}".format(
                            venue_code,
                            distance,
                            grade_name))
                        # print(complexity)
                        metrics = Metric.objects.filter(
                            participant__race__chart__program__venue=venue,
                            participant__race__distance=distance,
                            participant__race__grade__name=grade_name,
                            final__isnull=False)
                        #
                        print(len(metrics))
                        race_key = "{}_{}_{}".format(venue_code, distance, grade_name)
                        # print(race_key)
                        root_filename = "{}_J48_C{}".format(
                            race_key,
                            complexity.replace(".", "_"))
                        arff_filename = "{}/{}.arff".format(
                            arff_directory,
                            root_filename)
                        print(arff_filename)
                        is_nominal = False
                        arff_file = self.create_arff(
                            arff_filename,
                            metrics,
                            is_nominal)
                        classifier = "weka.classifiers.trees.J48"
                        options = ["-C", complexity]
                        create_model(arff_file, classifier, options, root_filename)
        jvm.stop()
