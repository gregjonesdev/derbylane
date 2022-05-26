import datetime
import weka.core.jvm as jvm

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from pww.utilities.arff import get_testing_arff
from pww.utilities.classifiers import recommendations, classifiers
from pww.utilities.metrics import new_get_metrics
from rawdat.models import Race
from pww.models import BettingGrade, WekaModel
from miner.utilities.constants import focused_grades, betting_venues
from miner.utilities.urls import model_directory
from pww.utilities.ultraweka import make_predictions, get_model


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str)

    def get_race_key(self, venue_code, grade_name):
        return "{}_{}".format(
            venue_code,
            grade_name)

    def make_straight_predictions(self, venue_code, grade_name, today, tomorrow):
        for model_name in recommendations:

            if race_key in model_name:
                testing_metrics = new_get_metrics(
                    grade_name,
                    venue_code,
                    today,
                    tomorrow)
                testing_arff = get_testing_arff(
                    new_key,
                    testing_metrics)
                model = get_model(model_directory, model_name)
#                 make_predictions(
#                     model,
#                     testing_arff,
#                     classifier_name,
#                     is_nominal,
#                     recommendations[model_name])

    def handle(self, *args, **options):
        # jvm.start(
        # packages=True,
        # max_heap_size="5028m"
        # )
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        # for venue_code in betting_venues:
            # for grade_name in focused_grades[venue_code]:
                # race_key = self.get_race_key(venue_code, grade_name)

        for race in Race.objects.filter(chart__program__date__gte=today):
            print("{} {}".format(race.chart.program.venue.code, race.grade.name))
            try:
                betting_grade = BettingGrade.objects.get(
                    venue=race.chart.program.venue,
                    grade=race.grade)
                race_models = WekaModel.objects.filter(betting_grade=betting_grade)
                print(race_models)
                # self.make_straight_predictions(betting_grade)
                # self.make_
            except ObjectDoesNotExist:
                print("No betting grade")
                pass
                # for race in targeted_races:
                #     print("{} {} Race {} Grade {}".format(
                #         venue_code,
                #         race.chart.get_time_display(),
                #         race.number,
                #         race.grade.name
                #     ))

        # jvm.stop()
