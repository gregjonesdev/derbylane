

from django.core.management.base import BaseCommand
from rawdat.models import Race

from pww.utilities.metrics import calculate_scaled_race_metrics


class Command(BaseCommand):

    def handle(self, *args, **options):
        races = Race.objects.all()[:1]
        calculate_scaled_race_metrics(races[0])
