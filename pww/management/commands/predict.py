import sys
import weka.core.jvm as jvm
import weka.core.converters as conv
import weka.core.serialization as serialization
import datetime

from django.core.management.base import BaseCommand
from rawdat.models import Participant, Bet_Recommendation, Grade, Venue
from pww.utilities.weka import (
    create_model,
    get_prediction_list,
    get_prediction)
from miner.utilities.urls import arff_directory
from pww.utilities.arff import create_arff
from pww.utilities.metrics import (
    get_defined_training_metrics,
    get_scheduled_metrics,
)
prediction = {
    "WD_548_B": "WD_548_B_smo_104.model",
    "WD_548_C": "WD_548_C_smo_008.model",
    "TS_550_B": "TS_550_B_smo_051.model",
    "TS_550_C": "TS_550_C_smo_053.model",
    "SL_583_C": "SL_583_C_smo_025.model",

}


c_options = {
    "smo": {
        "WD_548_B": "0.05",
        "TS_550_A": "0.03",
        # "WD_548_C": "0.08",
        # "TS_550_B": "0.51",
        "TS_550_C": "0.02",
        # "SL_583_C": "0.25",
    },
    "j48": {
        "WD_548_B": "0.06",
        "WD_548_C": "0.05",
        "TS_550_A": "0.38",
        "TS_550_B": "0.03",
        "TS_550_C": "0.27",
    }

}



betting_venues = ["WD", "TS", "SL"]

betting_distances = {
    "WD": 548,
    "TS": 550,
    "SL": 583
}

betting_grades = {
    "WD": ["B", "C"],
    "TS": ["A", "B", "C"],
    "SL": ["C"],
}

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str)


    def assign_predictions(
        self,
        recommendation,
        training_metrics,
        scheduled_metrics):
        # string_c = None
        # try:
        #     string_c = c_options[classifier_name][race_key]
        # except KeyError:
        #     pass
        # if string_c:
        #     model_name = "{}.model".format(race_key)
        #
        training_arff_filename = "{}/train.arff".format(arff_directory)
        testing_arff_filename = "{}/test.arff".format(arff_directory)
        #     testing_arff_filename = "{}/test_{}.arff".format(
        #         arff_directory,
        #         race_key)

        training_arff = create_arff(
            training_arff_filename,
            training_metrics,
            True)
        testing_arff = create_arff(
            testing_arff_filename,
            scheduled_metrics,
            False)

        classifier_name = recommendation.classifier.lower()
        c_factor = str(recommendation.c_factor)
        race_key= "races"
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")
        model = create_model(training_arff, classifier_name, c_factor, race_key, loader)



        confidence_cutoff = recommendation.cutoff
        prediction_list = get_prediction_list(testing_arff, model, confidence_cutoff)
        if 'smo' in classifier_name:
            self.save_smo_predictions(prediction_list)
        elif 'j48' in classifier_name:
            self.save_j48_predictions(prediction_list)



    def save_smo_predictions(self, prediction_list):
        for uuid in prediction_list.keys():
            prediction = prediction_list[uuid]
            self.save_smo_prediction(uuid, prediction)

    def save_j48_predictions(self, prediction_list):
        for uuid in prediction_list.keys():
            prediction = prediction_list[uuid]
            self.save_j48_prediction(uuid, prediction)


    def save_j48_prediction(self, participant_uuid, prediction):
        participant = Participant.objects.get(uuid=participant_uuid)
        pred = get_prediction(participant)
        pred.j48 = int(prediction)
        pred.save()



    def save_smo_prediction(self, participant_uuid, prediction):
        # print("Save smo")
        participant = Participant.objects.get(uuid=participant_uuid)
        pred = get_prediction(participant)
        pred.smo = int(prediction)
        pred.save()




    def build_race_key(self, venue_code, distance, grade_name):
        return "{}_{}_{}".format(venue_code, distance, grade_name)



    def handle(self, *args, **options):
        try:
            target_day = datetime.datetime.strptime(
                sys.argv[3],
                '%Y-%m-%d')
        except IndexError:
            target_day = datetime.date.today()
        yesterday = target_day - datetime.timedelta(days=1)
        tomorrow = target_day + datetime.timedelta(days=1)
        jvm.start(packages=True, max_heap_size="5028m")
        for venue_code in betting_venues:
            distance = betting_distances[venue_code]
            for grade_name in betting_grades[venue_code]:
                race_key = self.build_race_key(venue_code, distance, grade_name)
                print(race_key)
                grade = Grade.objects.get(name=grade_name)
                venue = Venue.objects.get(code=venue_code)
                recommendations = Bet_Recommendation.objects.filter(
                    venue=venue,
                    grade=grade,
                    distance=distance)

                scheduled_metrics = get_scheduled_metrics(
                    venue_code,
                    grade_name,
                    distance,
                    target_day,
                    tomorrow)

                if len(scheduled_metrics) > 0:
                    for recommendation in recommendations:
                        training_metrics = get_defined_training_metrics(
                            grade,
                            distance,
                            venue,
                            recommendation.start_date,
                            recommendation.months)
                        print(len(training_metrics))
                        self.assign_predictions(
                            recommendation,
                            training_metrics,
                            scheduled_metrics)

        jvm.stop()
