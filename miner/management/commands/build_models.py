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
            start_date = model["start_date"]
            end_date = model["end_date"]
            venue_code = model["venue_code"]
            grade_name = model["grade_name"]
            print(start_date)
            print(end_date)
            print(venue_code)
            print(grade_name)
            print(self.get_model_name(venue_code, grade_name, start_date))
            print("\n")
