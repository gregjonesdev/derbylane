import datetime


from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from pww.utilities.arff import get_prediction_arff
from pww.utilities.classifiers import recommendations
from pww.utilities.metrics import get_training_metrics
from rawdat.models import Venue
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
        # start_jvm()
        start_date = datetime.datetime(2015, 1, 1)
        end_date = datetime.datetime(2020, 12, 31)
        for venue in Venue.objects.filter(is_active=True):
            print(venue.code)
            for weka_model in WekaModel.objects.filter(venue=venue):
                print("Grade: {}".format(weka_model.grade.name))
                metrics = get_training_metrics(
                    weka_model.grade.name,
                    venue.code,
                    start_date,
                    end_date)
                print(len(metrics))

        # print("scheduled_metrics")
        # print(scheduled_metrics.count())
        # for race in Race.objects.filter(chart__program__date__gte=today):
        #     print(race.number)
        #     grade = race.grade
        #     venue = race.chart.program.venue
        #     weka_models = WekaModel.objects.filter(
        #         venue=venue,
        #         grade=grade
        #     )
        #     print("Weka models: {}".format(weka_models.count()))
        #     if weka_models.count() > 0:
        #         graded_metrics = scheduled_metrics.filter(
        #             participant__race__chart__program__venue=venue,
        #             participant__race__grade=grade)
        #         print("Graded Mterics: {}".format(len(graded_metrics)))
        #         for weka_model in weka_models:
        #             print(weka_model.get_name())
        #             self.make_straight_predictions(
        #                 race,
        #                 weka_model,
        #                 graded_metrics)

        # stop_jvm()
