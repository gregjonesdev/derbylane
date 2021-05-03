import os

from django.core.management.base import BaseCommand

import weka.core.jvm as jvm
import weka.core.converters as conv

from weka.classifiers import Evaluation, Classifier
from weka.core.classes import Random

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Weka script..")
        jvm.start(packages=True)
        data = conv.load_any_file("./rawdat/arff/airline.arff")
        print(data)
        jvm.stop()
