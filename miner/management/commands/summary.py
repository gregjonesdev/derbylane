
from django.core.management.base import BaseCommand
from datetime import datetime
from rawdat.models import Race, Program
from miner.utilities.urls import build_race_results_url
from miner.utilities.scrape import (
    get_node_elements,
    get_rows_of_length,
    save_single_bets,
    get_single_bets
)
import sys
from rawdat.models import Participant


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str)

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
        print(table_string.format("\t", "Win", "Place", " "))
        for grade in winnings.keys():
            grade_winnings = winnings[grade]
            self.write_table_row(grade, grade_winnings, table_string)
        print("\n")

    def write_table_row(self, grade, grade_winnings, table_string):
        print(table_string.format(
            grade,
            "{} ({})".format(
                self.get_average(grade_winnings["W"]),
                len(grade_winnings["W"])),
            "{} ({})".format(
                self.get_average(grade_winnings["P"]),
                len(grade_winnings["P"])),
            ""))

    def print_straight_wager_table(self, race):
        print("{}\t\t\t{}\t{}\t{}".format(
            " ",
            "Win",
            "Place",
            "Show"
        ))
        for participant in race.participant_set.filter(final__lte=3).order_by("final"):
            straight_wager = participant.straight_wager
            print("{}\t\t{}\t{}\t{}".format(
                "{} {}".format(participant.post, participant.dog.name[:8]),
                straight_wager.win,
                straight_wager.place,
                straight_wager.show
            ))
            print("\n")

    def handle(self, *args, **options):
        str_date = sys.argv[3]
        target_date = datetime.strptime(str_date, '%Y-%m-%d')
        print("\nAnalysis for: {}\n".format(target_date))
        for program in Program.objects.filter(date=target_date):
            for chart in program.chart_set.all():
                if chart.has_bets():
                    print("{}\n".format(
                        chart.get_kiosk_name()))
                    for race in chart.race_set.all():
                        if race.has_bets():
                            print("Race {}:\n".format(race.number))
                        # self.print_straight_wager_table(race)
                            for participant in race.participant_set.all():
                                if participant.bet_set.count():
                                    print(participant.dog.name)
        # last_week = yesterday = (today - datetime.timedelta(days=7))
        # winnings = {}
        # for participant in Participant.objects.filter(
        #     final__isnull=False,
        #     race__chart__program__date__gt=last_week):
        #     recommended_bets = participant.get_recommended_bet()
        #     if recommended_bets:
        #         race_key = self.get_race_key_from_race(participant.race)
        #         if not race_key in winnings.keys():
        #             winnings[race_key] = {"W": [], "P": [], "S":[]}
        #         if "W" in recommended_bets:
        #             winnings[race_key]["W"].append(
        #                 self.get_win_return(participant))
        #         if "P" in recommended_bets:
        #             winnings[race_key]["P"].append(
        #                 self.get_place_return(participant))
        #         if "S" in recommended_bets:
        #             winnings[race_key]["P"].append(
        #                 self.get_place_return(participant))
        # self.build_table(winnings)
