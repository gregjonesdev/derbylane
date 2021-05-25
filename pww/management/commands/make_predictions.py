import datetime
import csv
from django.core.exceptions import ObjectDoesNotExist

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
                    # relevant_metrics = self.get_relevant_metrics(venue, grade_name, distance)
                    print("{} Grade {} {} yds".format(venue.name, grade_name, distance))
                    print(len(graded_metrics))
                    # print(len(relevant_metrics))
                    # relevant_metrics = self.get_relevant_metrics(venue, grade_name, distance)
                    completed_metrics = graded_metrics.filter(final__isnull=False)
                    scheduled_metrics = graded_metrics.filter(final__isnull=True)




# get a list of participants in races for a specific venue, grade, and distance
# get a list of metrics for each participant
# get the relevant completed metrics
# send the two lists to pww for prediction(s)
