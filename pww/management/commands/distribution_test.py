import datetime
import sys

import weka.core.converters as conv
import weka.core.jvm as jvm

from time import time
from django.core.management.base import BaseCommand

from miner.utilities.constants import focused_distances
from miner.utilities.common import get_race_key, two_digitizer

from pww.utilities.ultraweka import get_metrics
from pww.utilities.testing import get_daily_results


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str)
        parser.add_argument('--venue', type=str)
        parser.add_argument('--grade', type=str)
        parser.add_argument('--prediction', type=int)


    def handle(self, *args, **options):
        start_time = time()
        classifier_name = sys.argv[3]
        venue_code = sys.argv[5]
        grade_name = sys.argv[7]
        prediction = sys.argv[9]
        distance = focused_distances[venue_code][0]
        target_date = "2021-12-29"
        all_metrics = get_metrics(
            venue_code,
            distance,
            grade_name)
        race_key = get_race_key(
            venue_code,
            distance,
            grade_name)



        jvm.start(packages=True, max_heap_size="5028m")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")
        print("\n")
        print("Model: {}\tVenue: {}\tGrade: {}\n".format(
            classifier_name,
            venue_code,
            grade_name
        ))

        get_daily_results(
            classifier_name,
            race_key,
            target_date,
            all_metrics,
            prediction,
            loader)


        jvm.stop()
        end_time = time()
        seconds_elapsed = end_time - start_time
        hours, rest = divmod(seconds_elapsed, 3600)
        minutes, seconds = divmod(rest, 60)

        print("\nCompleted Analysis in {}:{}:{}".format(
        two_digitizer(int(hours)),
        two_digitizer(int(minutes)),
        two_digitizer(int(seconds))))
