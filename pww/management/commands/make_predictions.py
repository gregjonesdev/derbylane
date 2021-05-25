import datetime
import csv
from django.core.exceptions import ObjectDoesNotExist
import os.path
from pathlib import Path
from django.core.management.base import BaseCommand
from rawdat.models import Race, Venue
from pww.models import Prediction, Metric


from miner.utilities.constants import (
    valued_grades,
    chart_times,
    venue_distances)
from pww.utilities.metrics import build_race_metrics


class Command(BaseCommand):


    def analyze_participants(self, race):
        for participant in race.participant_set.all():
            try:
                metric = Metric.objects.get(participant=participant)
            except:
                print("Metric not found for participant: {}".format(participant.uuid))

    def create_csv(self, filename, metrics):
        print("create csv()")
        print(filename)
        # nested_dir = date.replace("_", "/")
        #
        #
        # Path(csv_directory).mkdir(
        #         parents=True,
        #         exist_ok=True)
        raise SystemExit(0)
        with open("{}/{}".format(csv_directory, filename), 'w', newline='') as write_obj:
            csv_writer = csv.writer(write_obj)
            csv_writer.writerow(get_column_names())
            for metric in metrics:
                while len(metric) < len(coded_columns):
                    metric.append(0)
                # print(metric)
                csv_writer.writerow(metric)
        # print("done!")


    def handle(self, *args, **options):
        # filename = '/media/greg/85b2a17a-2087-4963-8d42-f1720b3be0d1/greg/work/derbylane/dl_env/derbylane/scheduled.csv'
        # with open(filename, 'r') as f:
        #     reader = csv.reader(f)
        #     for row in reader:
        #         print(row)
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
                    print("{} Grade {} {} yds".format(venue.name, grade_name, distance))
                    # print(len(graded_metrics))
                    completed_metrics = graded_metrics.filter(final__isnull=False)
                    scheduled_metrics = graded_metrics.filter(final__isnull=True)
                    print(len(completed_metrics))
                    print(len(scheduled_metrics))
                    race_key = "{}_{}_{}".format(venue.code, distance, grade_name)
                    self.create_csv("{}_scheduled.csv".format(race_key), scheduled_metrics)




# get a list of participants in races for a specific venue, grade, and distance
# get a list of metrics for each participant
# get the relevant completed metrics
# send the two lists to pww for prediction(s)
