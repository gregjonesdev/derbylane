from django.core.management.base import BaseCommand

from pww.utilities.classifiers import model_data

class Command(BaseCommand):

    def get_model_name(self, venue_code, grade_name, start_date):
        return "{}_{}_{}".format(
            venue_code,
            grade_name,
            start_date.replace("-", "_")
        )

    def handle(self, *args, **options):
        for model in model_data:
            print(model["start_date"])
            print(model["end_date"])
            print(model["venue_code"])
            print(model["grade_name"])
            print(self.get_model_name(model["venue_code"], model["grade_name"], model["start_date"]))
            print("\n")
