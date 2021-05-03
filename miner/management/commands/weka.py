import os

from django.core.management.base import BaseCommand

import weka.core.jvm as jvm
import weka.core.converters as conv

from weka.classifiers import Evaluation, Classifier
from weka.core.classes import Random

confidence_vector = "0.3"

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Weka script..\n")
        jvm.start(packages=True)
        data = conv.load_any_file("./rawdat/arff/weather.numeric.arff")
        data.class_is_last()
        cls = Classifier(
            classname="weka.classifiers.trees.J48",
            options=["-C", "0.3"])
        evl = Evaluation(data)
        evl.crossvalidate_model(cls, data, 10, Random(1))
        self.stdout.write(evl.summary("=== J48 on weather (numeric): Stats ===", False))
        self.stdout.write(evl.matrix("=== J48 on weather (numeric): Confusion Matrix"))
        jvm.stop()
