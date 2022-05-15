from django.core.management.base import BaseCommand

from pww.utilities.constants import model_data

class Command(BaseCommand):

    def handle(self, *args, **options):
        for model in model_data:
            print(model["start_date"])
            print(model["end_date"])
            print(model["venue_code"])
            print(model["grade_name"])
