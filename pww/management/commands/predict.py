import datetime


from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from pww.utilities.arff import get_prediction_arff
from pww.utilities.classifiers import recommendations
from pww.utilities.metrics import get_scheduled_metrics
from rawdat.models import Race
from pww.models import BettingGrade, WekaModel
from miner.utilities.urls import model_directory
from pww.utilities.ultraweka import (
    make_predictions,
    get_model,
    start_jvm,
    stop_jvm)


class Command(BaseCommand):

    def make_straight_predictions(self, race, weka_model, graded_metrics):
        # print("Straight predcition")
        # print(weka_model.__dict__)
        # print(weka_model.training_start)
        # print(weka_model.training_end)
        # print(weka_model.classifier.name)
        # print(weka_model.classifier.is_nominal)
        model = get_model(model_directory, weka_model.get_name())
        classifier = weka_model.classifier
        make_predictions(
            model,
            get_prediction_arff(graded_metrics),
            classifier.name,
            classifier.is_nominal,
            recommendations[model_name])



    def handle(self, *args, **options):
        start_jvm()
        today = datetime.date.today()
        scheduled_metrics = get_scheduled_metrics(today)
        for race in Race.objects.filter(chart__program__date__gte=today):
            grade = race.grade
            venue = race.chart.program.venue
            try:
                betting_grade = BettingGrade.objects.get(
                    venue=venue,
                    grade=grade)
                graded_metrics = scheduled_metrics.filter(
                    participant__race__chart__program__venue=venue,
                    participant__race__grade=grade)
                for weka_model in WekaModel.objects.filter(
                    betting_grade=betting_grade):
                    self.make_straight_predictions(
                        race,
                        weka_model,
                        graded_metrics)
            except ObjectDoesNotExist:
                pass
        stop_jvm()
