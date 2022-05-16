import datetime

from django.core.management.base import BaseCommand

from pww.utilities.arff import get_testing_arff
from pww.utilities.classifiers import recommendations
from pww.utilities.metrics import new_get_training_metrics
from rawdat.models import Race, Program
from miner.utilities.constants import focused_grades, betting_venues
from miner.utilities.urls import model_directory
from pww.utilities.ultraweka import make_predictions, get_model


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str)

    def handle(self, *args, **options):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        classifier_name = "smoreg"
        for venue_code in betting_venues:
            for grade_name in focused_grades[venue_code]:
                new_key = "{}_{}".format(
                    venue_code,
                    grade_name)
                for model_name in recommendations:
                    if new_key in model_name:
                        testing_metrics = new_get_training_metrics(
                            grade_name,
                            venue_code,
                            today,
                            tomorrow)
                        testing_arff = get_testing_arff(
                            "{}_{}".format(venue_code, grade_name),
                            testing_metrics)
                        model = get_model(
                            venue_code,
                            grade_name,
                            model_name["start"].replace("-", "_"),
                            model_directory,
                            model_name)
                        make_predictions(model, testing_arff, classifier_name)
