from django.core.management.base import BaseCommand

from pww.models import Metric

from rawdat.models import Grade, Venue

from django.core.exceptions import ObjectDoesNotExist


data = [
    {
        "venue": "TS",
        "distance": 550,
        "grade": "A",
        "prediction": 0.0,
        "win": 1.04,
        "place": None,
        "show": None,

    },
    {
        "venue": "WD",
        "distance": 548,
        "grade": "AA",
        "prediction": 0.0,
        "win": 1.27,
        "place": 1.10,
        "show": None,

    },
    {
        "venue": "WD",
        "distance": 548,
        "grade": "AA",
        "prediction": 1.0,
        "win": None,
        "place": 1.04,
        "show": None,

    },
    {
        "venue": "WD",
        "distance": 548,
        "grade": "A",
        "prediction": 0.0,
        "win": 1.22,
        "place": None,
        "show": None,

    },
    {
        "venue": "WD",
        "distance": 548,
        "grade": "A",
        "prediction": 0.0,
        "win": None,
        "place": 1.02,
        "show": None,

    },
    {
        "venue": "WD",
        "distance": 548,
        "grade": "B",
        "prediction": 0.0,
        "win": 1.06,
        "place": None,
        "show": None,

    },



]

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("build bet margins")
