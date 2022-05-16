import weka.core.jvm as jvm

from django.core.management.base import BaseCommand

from pww.models import Metric, Prediction
from pww.utilities.arff import get_training_arff
from pww.utilities.classifiers import model_data, recommendations
from pww.utilities.metrics import new_get_training_metrics
from pww.utilities.ultraweka import save_model, get_model_name

model_directory = "weka_models"

class Command(BaseCommand):

    def build_smoreg_model(self, classifier_name, venue_code, grade_name, start_date, end_date):
        pass

    def handle(self, *args, **options):
        jvm.start(
        packages=True,
        max_heap_size="5028m"
        )
        classifier_name = "smoreg"
        i = 1
        for model in model_data:
            print("building model {} of {}".format(i, len(model_data)))
            start_date = model["start_date"]
            end_date = model["end_date"]
            venue_code = model["venue_code"]
            grade_name = model["grade_name"]
            model_name = get_model_name(venue_code, grade_name, start_date)
            training_metrics = new_get_training_metrics(
                grade_name,
                venue_code,
                start_date,
                end_date)
            training_arff = get_training_arff(
                classifier_name,
                training_metrics)
            save_model(
                training_arff,
                classifier_name,
                model_name)
            i += 1
        jvm.stop()
