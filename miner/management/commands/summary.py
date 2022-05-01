
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
        win_bets = []
        place_bets = []
        show_bets = []
        for participant in race.participant_set.all():
            if participant.has_prediction():
                print("{}\t{}".format(
                "{}-{}".format(participant.post, participant.dog.name),

                ))

    def get_bet_returns(self, list):
        print(list)
        if list and len(list) > 0:
            return round((sum(list) - 2*len(list)), 2)
        else:
            return 0

    def handle(self, *args, **options):
        str_date = sys.argv[3]
        target_date = datetime.strptime(str_date, '%Y-%m-%d')
        print("\nAnalysis for: {}\n".format(target_date))
        graded_results = {}
        graded_predictions = {}
        for program in Program.objects.filter(date=target_date):
            for chart in program.chart_set.all():
                if chart.has_predictions():
                    print("{}\n".format(
                        chart.get_kiosk_name()))
                    for race in chart.race_set.all():
                        if race.has_predictions():
                            # print("Race {}:\n".format(race.number))
                            grade_name = race.grade.name
                            if not grade_name in graded_results.keys():
                                graded_results[grade_name] = {
                                    "W": [],
                                    "P": [],
                                    "S": []}
                                for participant in race.participant_set.all():
                                    if participant.get_recommended_bet():
                                        straight_wager = participant.straight_wager
                                        try:
                                            graded_results[grade_name]["W"].append(straight_wager.win if straight_wager.win  else 0)
                                            graded_results[grade_name]["P"].append(straight_wager.place if straight_wager.place else 0)
                                            graded_results[grade_name]["S"].append(straight_wager.show if straight_wager.show else 0)
                                        except:
                                            pass

        print("{}\t{}\t{}\t{}".format(
            "Grade",
            "Win",
            "Place",
            "Show"
        ))

        totals = {
            "W": [],
            "P": [],
            "S": []
        }
        for grade in graded_results:
            graded_wins = self.get_bet_returns(graded_results[grade_name]["W"])
            graded_places = self.get_bet_returns(graded_results[grade_name]["P"])
            graded_shows = self.get_bet_returns(graded_results[grade_name]["S"])
            totals["W"].append(graded_wins)
            totals["P"].append(graded_places)
            totals["S"].append(graded_shows)
            print("Grade: {}".format(grade))
            print("{}\t{}\t{}\t{}".format(
                grade,
                graded_wins,
                graded_places,
                graded_shows
            ))
        print("{}\t{}\t{}\t{}".format(
            "Total:",
            sum(totals["W"]),
            sum(totals["P"]),
            sum(totals["S"]))
        )



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
