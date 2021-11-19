
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

    def get_race_key_from_race(self, race):
        return "{}_{}_{}".format(
            race.chart.program.venue.code,
            race.distance,
            race.grade.name)


    def get_win_return(self, participant):
        try:
            return float(participant.straight_wager.win)
        except:
            return 0

    def get_place_return(self, participant):
        try:
            return float(participant.straight_wager.place)
        except:
            return 0

    def get_show_return(self, participant):
        try:
            return float(participant.straight_wager.show)
        except:
            return 0

    def get_average(self, list):
        if len(list) > 0:
            return round(sum(list)/len(list), 2)
        return "---"
    def build_table(self, winnings):
        print("\nReturns By Race Type:\n")
        table_string = "{}\t\t{}\t\t{}\t\t{}"
        print(table_string.format("\t", "Win", "Place", "Show"))
        for grade in winnings.keys():
            grade_winnings = winnings[grade]
            self.write_table_row(grade, grade_winnings, table_string)

    def write_table_row(self, grade, grade_winnings, table_string):
        print(table_string.format(
            grade,
            self.get_average(grade_winnings["W"]),
            self.get_average(grade_winnings["P"]),
            self.get_average(grade_winnings["S"])))

    def handle(self, *args, **options):

        today = datetime.date.today()
        yesterday = (today - datetime.timedelta(days=1))
        last_week = yesterday = (today - datetime.timedelta(days=7))
        winnings = {}
        for participant in Participant.objects.filter(
            final__isnull=False,
            race__chart__program__date__gt=last_week):
            recommended_bets = participant.get_recommended_bet()
            if recommended_bets:
                race_key = self.get_race_key_from_race(participant.race)
                if not race_key in winnings.keys():
                    winnings[race_key] = {"W": [], "P": [], "S":[]}
                if "W" in recommended_bets:
                    winnings[race_key]["W"].append(
                        self.get_win_return(participant))
                if "P" in recommended_bets:
                    winnings[race_key]["P"].append(
                        self.get_place_return(participant))
                if "S" in recommended_bets:
                    winnings[race_key]["P"].append(
                        self.get_place_return(participant))
        self.build_table(winnings)
