

from django.core.management.base import BaseCommand
from rawdat.models import Race

from pww.utilities.metrics import calculate_scaled_race_metrics

from scipy.optimize import curve_fit
from numpy import arange

def objective(x, a, b, c, d):
    return a*x + b*x**2 + c*x**3 + d


class Command(BaseCommand):

    def handle(self, *args, **options):

        races = Race.objects.filter(chart__program__date="2021-05-13", chart__program__venue__code="WD")[:1]
        # print(races)
        # calculate_scaled_race_metrics(races[0])
        for p in races[0].participant_set.all():
            target_date = p.race.chart.program.date
            whelp_date = p.dog.whelp_date
            age = target_date - target_date
            print(age.days)
            print(type(target_date))
        raise SystemExit(0)







        x_values = [1, 2, 3, 5, 6]
        y_values = [2, 4, 6, 10, 12]

        popt, _ = curve_fit(objective, x_values, y_values)

        a, b, c, d = popt
        y = objective(4, float(a), float(b), float(c), float(d))
        print(y)
