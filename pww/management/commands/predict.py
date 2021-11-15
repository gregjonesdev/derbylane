# import csv
import sys
import os
import fnmatch
from pathlib import Path
import weka.core.jvm as jvm
import weka.core.converters as conv
import weka.core.serialization as serialization
import datetime

from django.core.management.base import BaseCommand
from weka.classifiers import Classifier
from pww.models import Metric
from rawdat.models import Participant
from pww.utilities.ultraweka import (
    create_model,
    build_scheduled_data,
    get_uuid_line_index,
    get_prediction_list,
    get_prediction)
from miner.utilities.urls import arff_directory
from miner.utilities.constants import (
    focused_distances,
    focused_grades)
from pww.utilities.arff import create_arff

prediction_models = {
    "WD_548_B": "WD_548_B_smo_104.model",
    "WD_548_C": "WD_548_C_smo_008.model",
    "TS_550_B": "TS_550_B_smo_051.model",
    "TS_550_C": "TS_550_C_smo_053.model",
    "SL_583_C": "SL_583_C_smo_025.model",

}

c_options = {
    "WD_548_B": "1.04",
    "WD_548_C": "0.08",
    "TS_550_B": "0.51",
    "TS_550_C": "0.53",
    "SL_583_C": "0.25",

}



betting_venues = ["WD", "TS", "SL"]

betting_distances = {
    "WD": 548,
    "TS": 550,
    "SL": 583
}

betting_grades = {
    "WD": ["B", "C"],
    "TS": ["B", "C"],
    "SL": ["C"],
}

class Command(BaseCommand):





    def assign_predictions(self, training_metrics, prediction_metrics, race_key):
        model_name = prediction_models[race_key]
        print("For race_key {} use model {}".format(race_key, model_name))
        classifier_name = 'smo'
        string_c = c_options[race_key]
        training_arff_filename = "{}/train_{}.arff".format(
            arff_directory,
            race_key)
        testing_arff_filename = "{}/test_{}.arff".format(
            arff_directory,
            race_key)
        is_nominal = False
        # print("training metrics: {}".format(len(training_metrics)))
        training_arff = create_arff(
            training_arff_filename,
            training_metrics,
            is_nominal,
            True)
        testing_arff = create_arff(
            testing_arff_filename,
            prediction_metrics,
            is_nominal,
            False)

        jvm.start(packages=True, max_heap_size="5028m")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")
        model_name = create_model(training_arff, classifier_name, string_c, race_key, loader)
        self.make_predictions(model_name, testing_arff, loader)



    def make_predictions(self, model_name, testing_arff, loader):
        model = Classifier(jobject=serialization.read(model_name))
        uuid_line_index = get_uuid_line_index(testing_arff)
        testing_data = build_scheduled_data(testing_arff)
        prediction_list = get_prediction_list(model, testing_data, uuid_line_index)


        for uuid in prediction_list.keys():
            print(uuid)
            prediction = prediction_list[uuid]
            print(int(prediction))
            self.save_smo_prediction(uuid, prediction)


    def save_smo_prediction(self, participant_uuid, prediction):
        participant = Participant.objects.get(uuid=participant_uuid)
        pred = get_prediction(participant)
        pred.smo = int(prediction)
        pred.save()
        print(pred.__dict__)




    def build_race_key(self, venue_code, distance, grade_name):
        return "{}_{}_{}".format(venue_code, distance, grade_name)



    def handle(self, *args, **options):
        start_date = "2019-01-01"
        today = datetime.date.today()
        for venue_code in betting_venues:
            distance = betting_distances[venue_code]
            venue_metrics = Metric.objects.filter(
                participant__race__distance=distance,
                participant__race__chart__program__venue__code=venue_code,
                participant__race__chart__program__date__gte=start_date)
            for grade_name in betting_grades[venue_code]:
                graded_metrics = venue_metrics.filter(
                    participant__race__grade__name=grade_name)
                training_metrics = graded_metrics.filter(
                    participant__race__chart__program__date__lt=today)
                prediction_metrics = graded_metrics.filter(
                    participant__race__chart__program__date=today)

                race_key = self.build_race_key(venue_code, distance, grade_name)
                if len(prediction_metrics) > 0:
                    self.assign_predictions(
                            training_metrics,
                            prediction_metrics,
                            race_key)

        jvm.stop()
