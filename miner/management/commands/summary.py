
from django.core.management.base import BaseCommand
import datetime
from rawdat.models import Race
from miner.utilities.urls import build_race_results_url
from miner.utilities.scrape import (
    get_node_elements,
    get_rows_of_length,
    save_single_bets,
    get_single_bets
)
from rawdat.models import Participant


class Command(BaseCommand):

    def handle(self, *args, **options):

        today = datetime.date.today()
        yesterday = (today - datetime.timedelta(days=1))
        last_week = yesterday = (today - datetime.timedelta(days=7))
        print(today)
        for participant in Participant.objects.filter(
            race__chart__program__date__gte=last_week):
            recommended_bets = participant.get_recommended_bet()
            if recommended_bets:
                for bet in recommended_bets:
                    print("W" in bet)
                    print("P" in bet)
                    print("S" in bet)
