import datetime

from django.core.management.base import BaseCommand
from rawdat.models import Race, Venue
from pww.models import Prediction, Metric


from miner.utilities.constants import (
    valued_grades,
    chart_times,
    venue_distances)
from pww.utilities.metrics import build_race_metrics


class Command(BaseCommand):

    def get_relevant_metrics(self, venue, grade_name, distance):
        metrics = Metric.objects.filter(
            participant__race__chart__program__venue=venue,
            participant__race__distance=distance,
            participant__race__grade__name=grade_name
        )
        return metrics


    def handle(self, *args, **options):
        for venue in Venue.objects.filter(is_active=True):
            for distance in venue_distances[venue.code]:
                for grade_name in valued_grades:
                    races = Race.objects.filter(
                        chart__program__date=datetime.date.today(),
                        grade__name=grade_name,
                        distance=distance
                    )
                    print("{} Grade {} {} yds".format(venue.name, grade_name, distance))
                    print("----------------------------------")
                    relevant_metrics = self.get_relevant_metrics(venue, grade_name, distance)
                    completed_metrics = relevant_metrics.filter(final__isnull=False)
                    scheduled_metrics = relevant_metrics.filter(final__isnull=True)
                    print(len(relevant_metrics))
                    print("\n")
