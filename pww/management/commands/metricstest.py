

from django.core.management.base import BaseCommand
from rawdat.models import Race

from pww.utilities.metrics import build_race_metrics


class Command(BaseCommand):


    def handle(self, *args, **options):
        races = Race.objects.filter(chart__program__date="2021-04-17", chart__program__venue__code="WD")[:1]
        build_race_metrics(races[0])
