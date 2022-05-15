from django.core.management.base import BaseCommand

from pww.models import Metric, Prediction
from pww.utilities.classifiers import model_data


class Command(BaseCommand):

    def get_model_name(self, venue_code, grade_name, start_date):
        return "{}_{}_{}".format(
            venue_code,
            grade_name,
            start_date.replace("-", "_")
        )

    def build_smoreg_model(self, classifier_name, venue_code, grade_name, start_date, end_date):
        pass

    def handle(self, *args, **options):
        classifier_name = "smoreg"
        for model in model_data:
            start_date = model["start_date"]
            end_date = model["end_date"]
            venue_code = model["venue_code"]
            grade_name = model["grade_name"]
            print(self.get_model_name(venue_code, grade_name, start_date))

            training_metrics = Metric.objects.filter(
                participant__race__grade__name=grade_name,
                participant__race__chart__program__venue__code=venue_code,
                participant__race__chart__program__date__range=(
                    start_date,
                    end_date))

            print(len(training_metrics))
            print("\n")
