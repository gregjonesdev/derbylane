# import csv
import sys
import os
import fnmatch
from pathlib import Path
import weka.core.jvm as jvm
import datetime

from django.core.management.base import BaseCommand

from pww.models import Metric
from rawdat.models import Venue
# from pww.utilities.newweka import compare_predictions

from miner.utilities.constants import csv_columns

cells = 7
cell = "\t{}\t|"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Command(BaseCommand):

    def highlight_text(self, number):
        if number > 2.00:
            return bcolors.WARNING + bcolors.BOLD + "${}".format(number) + bcolors.ENDC
        else:
            return "${}".format(number)

    def handle(self, *args, **options):
        row_string = ""
        print("matrix")
        for i in range(cells):
            row_string += cell
        print(row_string.format(
            " ", "1", "2", "3", "4", "5", "6"
        ))
        print(row_string.format(
            "1", "$1.09", self.highlight_text(2.95), "$3.00", "$2.50", "$2.50", "$2.50"
        ))
        print(row_string.format(
            "2", "$1.09", "$2.90", "$3.00", "$2.50", "$2.50", "$2.50"
        ))
        print(row_string.format(
            "3", "$1.09", "$1.45", "$3.00", "$2.50", "$2.50", "$2.50"
        ))
        print(row_string.format(
            "4", "$1.09", "$2.90", "$3.00", "$2.50", "$2.50", "$2.50"
        ))
        print(row_string.format(
            "5", "$1.09", "$2.90", "$3.00", "$2.50", "$2.50", "$2.50"
        ))
        print(row_string.format(
            "6", "$1.09", "$2.90", "$3.00", "$2.50", "$2.50", "$2.50"
        ))
