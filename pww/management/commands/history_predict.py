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

    def make_straight_predictions(self, weka_model, prediction_metrics):
        classifier = weka_model.classifier
        make_predictions(
            weka_model,
            get_prediction_arff(prediction_metrics),
            classifier.is_nominal)



    def handle(self, *args, **options):
        start_jvm()
        start_date = datetime.datetime(2021, 1, 1)
        end_date = datetime.datetime(2022, 5, 31)
        for venue in Venue.objects.filter(is_active=True):
            print(venue.code)
            for weka_model in WekaModel.objects.filter(venue=venue):
                print("Grade: {}".format(weka_model.grade.name))
                prediction_metrics = get_training_metrics(
                    weka_model.grade.name,
                    venue.code,
                    start_date,
                    end_date)
                print(len(prediction_metrics))
                self.make_straight_predictions(
                    weka_model,
                    prediction_metrics)
        stop_jvm()
