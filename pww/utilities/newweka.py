import os

from django.core.management.base import BaseCommand
from weka.filters import Filter
import weka.core.jvm as jvm
import weka.core.converters as conv
from rawdat.models import Participant
from django.core.exceptions import ObjectDoesNotExist
from weka.classifiers import Evaluation, Classifier, FilteredClassifier
from weka.core.classes import Random
from pww.models import Prediction

# confidence_vector = "0.3"
data_dir = "./rawdat/arff/"

classifiers = [
    # "weka.classifiers.functions.SMO",
    # "weka.classifiers.trees.J48",
    "weka.classifiers.rules.ZeroR",
    "weka.classifiers.functions.SMOreg",
    "weka.classifiers.trees.REPTree",
    "weka.clusterers.SimpleKMeans",
    ]

def output_predictions(cls, data, uuid_list):
    print("Output predictions...")
    data.class_is_last()

    for index, inst in enumerate(data):
        # print("{} | {}".format(index, inst))
        pred = cls.classify_instance(inst)
        participant = Participant.objects.get(uuid=uuid_list[index])
        try:
            prediction = Prediction.objects.get(participant=participant)
        except ObjectDoesNotExist:
            new_prediction = Prediction(
                participant = participant
            )
            new_prediction.set_fields_to_base()
            new_prediction.save()
            prediction = new_prediction
        prediction.smo = pred
        prediction.save()
        # print("{}\t{}\t{}\t{}\t{}".format(
        #     participant.race.chart.program.date,
        #     participant.race.chart.time,
        #     participant.race.number,
        #     participant.dog.name,
        #     pred))
        # dist = cls.distribution_for_instance(inst)
        # print(
        # str(index+1) +
        # ": label index=" +
        # str(pred) +
        # ", class distribution=" +
        # str(dist))


# EXCLUDE Attribute without removing:
#  You can use the FilteredClassifier in conjunction with the Remove filter (weka.filters.unsupervised.attribute.Remove).
# remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "1,2,3,4,5"])




def train_classifier(data, classifier, options):
    print("Training classifier...")
    data.class_is_last()
    cls = Classifier(classname=classifier, options=options)
    print("Building classifier...")
    cls.build_classifier(data)
    return cls

def get_uuid_list(scheduled_csv):
    arff_file = open(scheduled_csv, "r")
    uuids = []
    for line in arff_file:
        if len(line) > 100:
            uuids.append(line.split(",")[0])
    return uuids

def make_predictions(arff_data):
    jvm.start(packages=True, max_heap_size="2048m")
    for each in arff_data:
        results_csv = each["results"]
        scheduled_csv = each["scheduled"]
        uuid_list = get_uuid_list(scheduled_csv)
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")
        results_data=loader.load_file(results_csv)
        scheduled_data=loader.load_file(scheduled_csv)
        remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "first"])
        remove.inputformat(results_data)
        # remove.inputformat(scheduled_data)
        filtered_results = remove.filter(results_data)   # filter the data
        filtered_scheduled = remove.filter(scheduled_data)
        cls = train_classifier(filtered_results, "weka.classifiers.functions.SMOreg", [])
        output_predictions(cls, filtered_scheduled, uuid_list)
    #
    jvm.stop()
