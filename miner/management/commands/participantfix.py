import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.core.management.base import BaseCommand

from miner.utilities.common import get_node_elements
from miner.utilities.scrape import parse_results_url
from miner.utilities.urls import build_race_results_url
from rawdat.models import Race

from pww.utilities.metrics import build_race_metrics


class Command(BaseCommand):

    def handle(self, *args, **options):
        for race in Race.obkects.all():
            if race.participant_set.count() > 10:
                print(race.uuid)
