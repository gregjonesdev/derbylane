import datetime


from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from pww.utilities.arff import get_prediction_arff
from pww.utilities.classifiers import recommendations
from pww.utilities.metrics import get_scheduled_metrics
from rawdat.models import Race
from pww.models import WekaModel
from miner.utilities.urls import model_directory
from pww.utilities.weka import (
    make_predictions,
    get_model,
    start_jvm,
    stop_jvm)


class Command(BaseCommand):

    def make_straight_predictions(self, race, weka_model, graded_metrics):
        print("Straight predcition")
        print(weka_model.training_start)
        print(weka_model.training_end)
        print(weka_model.classifier.name)
        classifier = weka_model.classifier
        print(weka_model)
        make_predictions(
            weka_model,
            get_prediction_arff(graded_metrics),
            classifier.is_nominal)



    def handle(self, *args, **options):
        start_jvm()
        today = datetime.date.today()
        scheduled_metrics = get_scheduled_metrics(today)
        for race in Race.objects.filter(chart__program__date__gte=today):
            print(race.number)
            grade = race.grade
            venue = race.chart.program.venue
            weka_models = WekaModel.objects.filter(
                venue=venue,
                grade=grade
            )
            if weka_models.count() > 0:
                graded_metrics = scheduled_metrics.filter(
                    participant__race__chart__program__venue=venue,
                    participant__race__grade=grade)
                print("Graded Mterics: {}".format(len(graded_metrics)))
                for weka_model in weka_models:
                    print(weka_model.get_name())
                    self.make_straight_predictions(
                        race,
                        weka_model,
                        graded_metrics)

        stop_jvm()
