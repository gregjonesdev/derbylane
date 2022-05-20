import sys
from weka.core.converters import Loader

import weka.core.jvm as jvm

from django.core.management.base import BaseCommand
from pww.models import Metric
from miner.utilities.constants import focused_grades
from pww.utilities.arff import (
    get_training_arff,
    get_testing_arff,
)
from pww.utilities.classifiers import classifiers
from pww.utilities.ultraweka import get_model, evaluate_exotics
from pww.utilities.weka import create_model
from pww.utilities.testing import evaluate_model_cutoffs, evaluate_nominal_model
from pww.utilities.metrics import new_get_metrics

betting_distances = {
    "WD": 548,
    "TS": 550,
    "SL": 583
}

model_directory = "test_models"


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str)
        parser.add_argument('--venue', type=str)
        parser.add_argument('--grade', type=str)
        parser.add_argument('--start', type=str)

    def handle(self, *args, **options):
        classifier_name = sys.argv[3]
        venue_code = sys.argv[5]
        grade_name = sys.argv[7]
        start_date = sys.argv[9]
        end_date = "2021-12-31"
        test_start = "2022-01-01"
        test_stop = "2022-04-20"
        training_metrics = new_get_metrics(
            grade_name,
            venue_code,
            start_date,
            end_date)
        training_arff = get_training_arff(
            classifier_name,
            training_metrics)
        jvm.start(
            packages=True,
            max_heap_size="5028m"
        )
        print("{} Grade {}".format (venue_code, grade_name))
        print("{} - {}".format(start_date, end_date))
        print("Training Metrics: {}\n".format(
            len(training_metrics)))

        testing_metrics = new_get_metrics(
            grade_name,
            venue_code,
            test_start,
            test_stop)
        testing_arff = get_testing_arff(
            "{}_{}".format(venue_code, grade_name),
            testing_metrics)
        print("Testing Metrics: {}".format(len(testing_metrics)))

        # Must build test model
        model = get_model(model_directory, "exotic_test")
        evaluate_exotics(
            testing_arff,
            model,
            classifier_name)
        jvm.stop()

    # def get_race_predictions(self, race):
    #     pass
    #
    # def evaluate_superfectas(
    #     self,
    #     testing_races,
    #     prediction_list,
    #     prediction_numbers):
    #
    #     scenario = "{}-{}-{}-{}".format(
    #         prediction_numbers[0],
    #         prediction_numbers[1],
    #         prediction_numbers[2],
    #         prediction_numbers[3])
    #
    #
    # def evaluate_trifectas(
    #     self,
    #     testing_races,
    #     prediction_list,
    #     prediction_numbers):
    #
    #     scenario = "{}-{}-{}".format(
    #         prediction_numbers[0],
    #         prediction_numbers[1],
    #         prediction_numbers[2])
    #
    #
    # def get_quiniela_return(
    #     self,
    #     testing_races,
    #     prediction_list,
    #     prediction_numbers):
    #
    #     bet_winnings = []
    #
    #     for race in testing_races:
    #         matches_predictions = self.get_matching_participants(
    #             race,
    #             prediction_numbers,
    #             prediction_list)
    #         matches_first = matches_predictions[0]
    #         matches_second = matches_predictions[1]
    #         unique_quinielas = self.get_unique_quinielas(
    #             matches_first,
    #             matches_second)
    #         for pair in unique_quinielas:
    #             bet_winnings.append(
    #                 self.get_quiniela_winnings(pair[0], pair[1]))
    #
    #     return bet_winnings
    #
    # def get_exacta_return(
    #     self,
    #     testing_races,
    #     prediction_list,
    #     prediction_numbers):
    #
    #     bet_winnings = []
    #
    #     for race in testing_races:
    #         matches_predictions = self.get_matching_participants(
    #             race,
    #             prediction_numbers,
    #             prediction_list)
    #         matches_first = matches_predictions[0]
    #         matches_second = matches_predictions[1]
    #         unique_exactas = self.get_unique_exactas(
    #             matches_first,
    #             matches_second)
    #         for pair in unique_exactas:
    #             bet_winnings.append(
    #                 self.get_exacta_winnings(pair[0], pair[1]))
    #
    #     return bet_winnings
    #
    # def get_trifecta_return(
    #     self,
    #     testing_races,
    #     prediction_list,
    #     prediction_numbers):
    #
    #     bet_winnings = []
    #
    #     for race in testing_races:
    #         matches_predictions = self.get_matching_participants(
    #             race,
    #             prediction_numbers,
    #             prediction_list)
    #         matches_first = matches_predictions[0]
    #         matches_second = matches_predictions[1]
    #         matches_third = matches_predictions[2]
    #         unique_trifectas = self.get_unique_trifectas(
    #             matches_first,
    #             matches_second,
    #             matches_third)
    #         for set in unique_trifectas:
    #             bet_winnings.append(
    #                 self.get_trifecta_winnings(set[0], set[1], set[2]))
    #
    #     return bet_winnings
    #
    # def get_average_return(self, bet_winnings):
    #     if len(bet_winnings) > 0:
    #         return float(round(sum(bet_winnings)/len(bet_winnings), 2))
    #     else:
    #         return 0
    #
    # def get_quiniela_winnings(self, participant_1, participant_2):
    #     quienla = None
    #     try:
    #         quienla = Quiniela.objects.get(
    #             left=participant_1,
    #             right=participant_2
    #         )
    #     except ObjectDoesNotExist:
    #         try:
    #             quienla = Quiniela.objects.get(
    #                 left=participant_2,
    #                 right=participant_1
    #             )
    #         except ObjectDoesNotExist:
    #             pass
    #     if quienla:
    #         return quienla.payout
    #     return 0
    #
    # def get_exacta_winnings(self, participant_1, participant_2):
    #     exacta = None
    #     try:
    #         exacta = Exacta.objects.get(
    #             win=participant_1,
    #             place=participant_2
    #         )
    #     except ObjectDoesNotExist:
    #         pass
    #     if exacta:
    #         return exacta.payout
    #     return 0
    #
    # def get_trifecta_winnings(self, participant_1, participant_2, participant_3):
    #     trifecta = None
    #     try:
    #         trifecta = Trifecta.objects.get(
    #             win=participant_1,
    #             place=participant_2,
    #             show=participant_3
    #         )
    #     except ObjectDoesNotExist:
    #         pass
    #     if trifecta:
    #         return trifecta.payout
    #     return 0
    #
    # def get_testing_metrics(self, testing_races):
    #     testing_metrics = []
    #     for race in testing_races:
    #         for participant in race.participant_set.all():
    #             try:
    #                 testing_metrics.append(participant.metric)
    #             except:
    #                 pass
    #     return testing_metrics
    #
    # def get_matching_participants(
    #     self,
    #     race,
    #     predictions,
    #     prediction_list):
    #     matches_1 = []
    #     matches_2 = []
    #     matches_3 = []
    #     matches_4 = []
    #     for participant in race.participant_set.all():
    #         try:
    #             str_uuid = str(participant.uuid)
    #             participant_prediction = prediction_list[str_uuid]
    #             int_pred = int(participant_prediction)
    #             if int_pred == predictions[0]:
    #                 matches_1.append(participant)
    #             elif int_pred == predictions[1]:
    #                 matches_2.append(participant)
    #             elif int_pred == predictions[2]:
    #                 matches_3.append(participant)
    #             elif int_pred == predictions[3]:
    #                 matches_4.append(participant)
    #         except:
    #             pass
    #     return [matches_1, matches_2, matches_3, matches_4]
    #
    #
    # def get_unique_quinielas(self, matches_first, matches_second):
    #     unique_quinielas = []
    #     i = 0
    #     while i < len(matches_first):
    #         first = matches_first[i]
    #         j = 0
    #         while j < len(matches_second):
    #             second = matches_second[j]
    #             if not first == second:
    #                 if not (first, second) in unique_quinielas:
    #                     if not (second, first) in unique_quinielas:
    #                         unique_quinielas.append((first, second))
    #             j += 1
    #         i += 1
    #
    #     return unique_quinielas
    #
    #
    # def get_unique_exactas(self, matches_first, matches_second):
    #     unique_exactas = []
    #     i = 0
    #     while i < len(matches_first):
    #         first = matches_first[i]
    #         j = 0
    #         while j < len(matches_second):
    #             second = matches_second[j]
    #             if not first == second:
    #                 if not (first, second) in unique_exactas:
    #                     unique_exactas.append((first, second))
    #             j += 1
    #         i += 1
    #
    #     return unique_exactas
    #
    # def get_unique_trifectas(self, matches_first, matches_second, matches_third):
    #     unique_trifectas = []
    #     i = 0
    #     while i < len(matches_first):
    #         first = matches_first[i]
    #         j = 0
    #         while j < len(matches_second):
    #             second = matches_second[j]
    #             k = 0
    #             while k < len(matches_third):
    #                 third = matches_third[k]
    #                 if not (
    #                     first == second or
    #                     first == third or
    #                     second == third):
    #                     if not (first, second, third) in unique_trifectas:
    #                         unique_trifectas.append((first, second, third))
    #                 k += 1
    #             j += 1
    #         i += 1
    #
    #     return unique_trifectas
    #
    # def get_potential(self, average_return, bet_winnings):
    #     if average_return > 2:
    #         return average_return*len(bet_winnings)
    #     else:
    #         return 0
    #
    # def get_success_rate(self, return_list):
    #     total_count = len(return_list)
    #     if total_count:
    #         correct_count = geek.count_nonzero(return_list)
    #         return (correct_count/total_count)
    #     return 0
    #
    # def get_optimal_quiniela(
    #     self,
    #     optimal_quiniela,
    #     testing_races,
    #     prediction_list,
    #     prediction_numbers):
    #     current_quiniela = self.get_quiniela_return(
    #         testing_races,
    #         prediction_list,
    #         prediction_numbers)
    #
    #     for each in prediction_list:
    #         print(prediction_list[each])
    #     average_return = self.get_average_return(current_quiniela)
    #     if average_return > 2:
    #         current_success_rate = self.get_success_rate(current_quiniela)
    #         current_potential = self.get_potential(average_return, current_quiniela)
    #         if current_success_rate > optimal_quiniela["success_rate"]:
    #         # if current_potential > optimal_quiniela["potential"]:
    #             return {
    #                 "scenario": "{}-{}".format(prediction_numbers[0], prediction_numbers[1]),
    #                 "average_return": average_return,
    #                 "potential": current_potential,
    #                 "success_rate": round(current_success_rate, 4)
    #             }
    #     return optimal_quiniela
    #
    # def get_optimal_exacta(
    #     self,
    #     optimal_exacta,
    #     testing_races,
    #     prediction_list,
    #     prediction_numbers):
    #     current_exacta = self.get_exacta_return(
    #         testing_races,
    #         prediction_list,
    #         prediction_numbers)
    #
    #     average_return = self.get_average_return(current_exacta)
    #     if average_return > 2:
    #         current_potential = self.get_potential(average_return, current_exacta)
    #         if current_potential > optimal_exacta["potential"]:
    #             return {
    #                 "scenario": "{}-{}".format(prediction_numbers[0], prediction_numbers[1]),
    #                 "average_return": average_return,
    #                 "potential": int(current_potential),
    #                 "success_rate": self.get_success_rate(current_exacta)
    #             }
    #     return optimal_exacta
    #
    # def get_optimal_trifecta(
    #     self,
    #     optimal_trifecta,
    #     testing_races,
    #     prediction_list,
    #     prediction_numbers):
    #     current_trifecta = self.get_trifecta_return(
    #         testing_races,
    #         prediction_list,
    #         prediction_numbers)
    #     average_return = self.get_average_return(current_trifecta)
    #     current_success_rate = self.get_success_rate(current_trifecta)
    #     if average_return > 2:
    #         if current_success_rate > optimal_trifecta["success_rate"]:
    #             current_potential = self.get_potential(average_return, current_trifecta)
    #             return {
    #                 "scenario": "{}-{}-{}".format(prediction_numbers[0], prediction_numbers[1], prediction_numbers[2]),
    #                 "average_return": average_return,
    #                 "potential": int(current_potential),
    #                 "success_rate": round(current_success_rate, 4)
    #             }
    #     return optimal_trifecta
    #
    # def print_optimal_bet(self, optimal_bet, bet_name):
    #     if optimal_bet["average_return"] > 0:
    #         print("Optimal {}:\t{}\t{}\t{}\t{}".format(
    #             bet_name,
    #             optimal_bet["scenario"],
    #             optimal_bet["average_return"],
    #             optimal_bet["potential"],
    #             "{}%".format(optimal_bet["success_rate"])))
    #
    #
    #
    # def print_returns(self, testing_races, prediction_list, c, race_key, cutoff_date, loader):
    #     prediction_numbers = [0, 0, 0, 0]
    #     highest_number = 5
    #     optimal_quiniela = {
    #         "scenario": "",
    #         "average_return": 0,
    #         "potential": 0,
    #         "success_rate": 0,
    #     }
    #     optimal_exacta = {
    #         "scenario": "",
    #         "average_return": 0,
    #         "potential": 0,
    #         "success_rate": 0,
    #     }
    #     optimal_trifecta = {
    #         "scenario": "",
    #         "average_return": 0,
    #         "potential": 0,
    #         "success_rate": 0,
    #     }
    #     while prediction_numbers[0] < highest_number:
    #         prediction_numbers[1] = 0
    #         while prediction_numbers[1] < highest_number:
    #             optimal_quiniela = self.get_optimal_quiniela(
    #                 optimal_quiniela,
    #                 testing_races,
    #                 prediction_list,
    #                 prediction_numbers)
    #             # optimal_exacta = self.get_optimal_exacta(
    #             #     optimal_exacta,
    #             #     testing_races,
    #             #     prediction_list,
    #             #     prediction_numbers)
    #             #
    #             # prediction_numbers[2] = 0
    #             # while prediction_numbers[2] < highest_number:
    #             #     optimal_trifecta = self.get_optimal_trifecta(
    #             #         optimal_trifecta,
    #             #         testing_races,
    #             #         prediction_list,
    #             #         prediction_numbers)
    #
    #
    #
    #                 # prediction_numbers[3] = 0
    #             #     while prediction_numbers[3] < highest_number:
    #             #         self.evaluate_superfectas(
    #             #             testing_races,
    #             #             prediction_list,
    #             #             prediction_numbers)
    #             #         prediction_numbers[3] += 1
    #
    #
    #
    #                 # prediction_numbers[2] += 1
    #             prediction_numbers[1] += 1
    #         prediction_numbers[0] += 1
    #
    #     self.print_optimal_bet(optimal_quiniela, "Quiniela")
    #     self.print_optimal_bet(optimal_exacta, "Exacta")
    #     self.print_optimal_bet(optimal_trifecta, "Trifecta")
    #
    #
