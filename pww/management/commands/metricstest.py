

from django.core.management.base import BaseCommand
from rawdat.models import Race, Participant

from pww.utilities.metrics import build_race_metrics, get_age
from pww.models import Prediction, Metric


class Command(BaseCommand):


    def handle(self, *args, **options):

        grade = "C"
        distance = 546
        venue_code = "CA"

        print("Querying metrics for: {} / {} / {}".format(
            venue_code,
            distance,
            grade))

        completed_metrics = Metric.objects.filter(
            final__isnull=False,
            participant__race__grade__name=grade,
            participant__race__distance=distance,
            participant__race__chart__program__venue__code=venue_code
        )

        print("Currently {} metrics available.".format(completed_metrics.count()))
