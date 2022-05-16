from django.core.management.base import BaseCommand

from pww.models import Metric, Prediction
from pww.utilities.classifiers import model_data, reccomendations
from pww.utilities.arff import get_training_arff
from pww.utilities.ultraweka import save_model
from pww.utilities.metrics import new_get_training_metrics
import weka.core.jvm as jvm


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
        jvm.start(
        packages=True,
        max_heap_size="5028m"
        )
        classifier_name = "smoreg"

        for model in model_data:
            start_date = model["start_date"]
            end_date = model["end_date"]
            venue_code = model["venue_code"]
            grade_name = model["grade_name"]
            model_name = self.get_model_name(venue_code, grade_name, start_date)
            training_metrics = new_get_training_metrics(
                grade_name,
                venue_code,
                start_date,
                end_date)
            print(len(training_metrics))
            training_arff = get_training_arff(
                classifier_name,
                training_metrics)
            # save_model(
            #     training_arff,
            #     classifier_name,
            #     model_name)
            for each in reccomendations[model_name]:
                print("{}\t{}\t{}".format(
                    model_name,
                    "{}-{}".format(
                        each["start"],
                        each["end"]),
                    each["bet"]
                ))
