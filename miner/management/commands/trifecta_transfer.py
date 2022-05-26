import datetime
import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from miner.utilities.common import get_node_elements
from miner.utilities.scrape import single_url_test
from miner.utilities.urls import build_race_results_url
from rawdat.models import Winning_Trifecta, Predicted_Trifecta, OldTrifecta
from pww.models import Prediction

from pww.utilities.metrics import build_race_metrics




class Command(BaseCommand):

    def handle(self, *args, **options):
        old_trifectas = OldTrifecta.objects.all()
        print("Old trifecta count: {}".format(len(old_trifectas)))
        for trifecta in old_trifectas:
            try:
                winning_trifecta = Winning_Trifecta.objects.get(
                    race = trifecta.race,
                    win = trifecta.win,
                    place = trifecta.place,
                    show = trifecta.show
                )
            except ObjectDoesNotExist:
                new_trifecta = Winning_Trifecta(
                    race = trifecta.race,
                    win = trifecta.win,
                    place = trifecta.place,
                    show = trifecta.show
                )
                winning_trifecta = new_trifecta
            winning_trifecta.payout = trifecta.payout
            winning_trifecta.set_fields_to_base()
            winning_trifecta.save()

        print("Winning Trifectas count: {}".format(Winning_Trifecta.objects.all().count()))
