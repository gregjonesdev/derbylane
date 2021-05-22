import os

from django.core.management.base import BaseCommand

import weka.core.jvm as jvm
import weka.core.converters as conv

from weka.classifiers import Evaluation, Classifier
from weka.core.classes import Random

confidence_vector = "0.3"
data_dir = "./rawdat/arff/"
class Command(BaseCommand):

    def build_attributes():
        attributes = []
        attributes.append(
            Attribute.create_numeric("scaled_fastest_time"))
        attributes.append(Attribute.create_nominal("sex", ["M", "F"]))
        return attributes

    def create_dataset(dataset_name):
        return Instances.create_instances(
            dataset_name,
            self.build_attributes(),
            0)

    def populate_dataset(query_instance):
        for metric in metrics:
        inst = Instance.create_instance(metrics)        
        dataset.add_instance(inst)


    def handle(self, *args, **options):
        self.stdout.write("Starting Weka script..\n")
        jvm.start(packages=True, system_info=True)
        # data = conv.load_any_file("./rawdat/arff/weather.numeric.arff")
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")
        data=loader.load_file(data_dir + "weather.numeric.arff")
        # data=loader.load_file(data_dir + "weather.numeric.arff", class_index="last")

        data.class_is_last()
        cls = Classifier(
            classname="weka.classifiers.trees.J48",
            options=["-C", "0.3"])
        evl = Evaluation(data)
        evl.crossvalidate_model(cls, data, 10, Random(1))
        self.stdout.write(evl.summary("=== J48 on weather (numeric): Stats ===", False))
        self.stdout.write(evl.matrix("=== J48 on weather (numeric): Confusion Matrix"))
        jvm.stop()
