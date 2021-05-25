import csv
import datetime

from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from pww.models import Prediction, Metric
from rawdat.models import Race, Venue


from miner.utilities.constants import (
    valued_grades,
    chart_times,
    venue_distances,
    csv_columns,
    )


class Command(BaseCommand):


    def create_csv(self, filename, metrics):
        csv_directory = "csv"
        Path(csv_directory).mkdir(
                parents=True,
                exist_ok=True)

        with open("{}/{}".format(csv_directory, filename), 'w', newline='') as write_obj:
            csv_writer = csv.writer(write_obj)
            csv_writer.writerow(csv_columns)
            for metric in metrics:
                csv_writer.writerow(metric.build_csv_metric())


    def handle(self, *args, **options):
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
                        self.create_csv("{}_scheduled.csv".format(race_key), scheduled_metrics)
