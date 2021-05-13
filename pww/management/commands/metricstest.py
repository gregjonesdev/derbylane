

from django.core.management.base import BaseCommand
from rawdat.models import Race

from pww.utilities.metrics import calculate_scaled_race_metrics

from scipy.optimize import curve_fit


class Command(BaseCommand):

    def handle(self, *args, **options):
        races = Race.objects.filter(chart__program__date="2021-05-12", chart__program__venue__code="WD")[:1]
        calculate_scaled_race_metrics(races[0])
