import datetime
import weka.core.jvm as jvm

from django.core.management.base import BaseCommand

from pww.utilities.arff import get_testing_arff
from pww.utilities.classifiers import recommendations, classifiers
from pww.utilities.metrics import new_get_metrics
from rawdat.models import Race, Program
from miner.utilities.constants import focused_grades, betting_venues
from miner.utilities.urls import model_directory
from pww.utilities.ultraweka import make_predictions, get_model


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str)

    def handle(self, *args, **options):
        # jvm.start(
        # packages=True,
        # max_heap_size="5028m"
        # )
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        classifier_name = "smoreg"
        is_nominal = False
        for venue_code in betting_venues:
            print(venue_code)
            for grade_name in focused_grades[venue_code]:
                targeted_races = Race.objects.filter(
                    chart__program__date__gte=today,
                    grade__name=grade_name,
                    chart__program__venue__code=venue_code)
                for race in targeted_races:
                    print("{} {} Race {} Grade {}".format(
                        venue_code,
                        race.chart.get_time_display(),
                        race.number,
                        race.grade.name
                    ))
        #         new_key = "{}_{}".format(
        #             venue_code,
        #             grade_name)
        #         for model_name in recommendations:
        #             if new_key in model_name:
        #                 testing_metrics = new_get_metrics(
        #                     grade_name,
        #                     venue_code,
        #                     today,
        #                     tomorrow)
        #                 testing_arff = get_testing_arff(
        #                     new_key,
        #                     testing_metrics)
        #                 model = get_model(model_directory, model_name)
        #                 make_predictions(
        #                     model,
        #                     testing_arff,
        #                     classifier_name,
        #                     is_nominal,
        #                     recommendations[model_name])
        # jvm.stop()
