import os

from django.core.management.base import BaseCommand
from weka.filters import Filter
import weka.core.jvm as jvm
import weka.core.converters as conv
import weka.core.serialization as serialization
from rawdat.models import Participant
from weka.classifiers import Evaluation, Classifier, FilteredClassifier
from weka.core.classes import Random

confidence_vector = "0.3"
data_dir = "./rawdat/arff/"

classifiers = [
    # "weka.classifiers.functions.SMO",
    # "weka.classifiers.trees.J48",
    "weka.classifiers.rules.ZeroR",
    "weka.classifiers.functions.SMOreg",
    "weka.classifiers.trees.REPTree",
    "weka.clusterers.SimpleKMeans",
    ]


def create_model(model_arff, race_key):
    jvm.start(packages=True, max_heap_size="2048m")
    print("weka create model")
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    print("here")
    unfiltered_data = loader.load_file(model_arff)
    print(unfiltered_data)
    remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "first"])
    remove.inputformat(unfiltered_data)
    filtered_data = remove.filter(unfiltered_data)
    filtered_data.class_is_last()
    cls = Classifier(classname="weka.classifiers.functions.SMOreg", options=[])
    cls.build_classifier(filtered_data)

    filename = "arff/{}.model".format(race_key)
    # classifier.build_classifier(...)
    # outfile = filename.model
    serialization.write(filename, cls)
    jvm.stop()

def predict(race_key):
    print("weka predict")
    print(race_key)
    # Read
    # model = Classifier(jobject=serialization.read(outfile))


def output_predictions(cls, data, uuid_list):
    data.class_is_last()

    for index, inst in enumerate(data):
        # print("{} | {}".format(index, inst))
        pred = cls.classify_instance(inst)
        participant = Participant.objects.get(uuid=uuid_list[index])
        print("{}\t{}\t{}\t{}\t{}".format(participant.race.chart.program.date, participant.race.chart.time, participant.race.number, participant.dog.name, pred))
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
    data.class_is_last()
    cls = Classifier(classname=classifier, options=options)
    cls.build_classifier(data)
    return cls

def get_uuid_list(scheduled_csv):
    arff_file = open(scheduled_csv, "r")
    uuids = []
    for line in arff_file:
        if len(line) > 100:
            uuids.append(line.split(",")[0])
    return uuids


def process_classifier(name, options, uuid_list, results, scheduled):
    print("process {}".format("name"))
    cls = train_classifier(results, name, options)
    # output_predictions(cls, scheduled, uuid_list)



def make_predictions(arff_data):
    print("make predcitions")
    jvm.start(packages=True, system_info=True, max_heap_size="512m")

    super_classifiers = [
        {
            "name": "weka.classifiers.functions.SMOreg",
            "options": [],
            "is_nominal": False
        },
        # {
        #     "name": "weka.classifiers.trees.J48",
        #     "options": [],
        #     "is_nominal": True
        # },


    ]
    for each in arff_data:
        results_csv = each["results"]
        scheduled_csv = each["scheduled"]
        nominal_csv = each["nominal"]
        print(scheduled_csv)
        print(results_csv)
        uuid_list = get_uuid_list(scheduled_csv)
        loader = conv.Loader(classname="weka.core.converters.ArffLoader")

        results_data=loader.load_file(results_csv)
        nominal_results_data = loader.load_file(nominal_csv)
        scheduled_data=loader.load_file(scheduled_csv)

        classifier = "weka.classifiers.functions.SMOreg"


        remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "first"])
        remove.inputformat(results_data)
        remove.inputformat(nominal_results_data)
        remove.inputformat(scheduled_data)

        filtered_results = remove.filter(results_data)
        filtered_nominal_results = remove.filter(nominal_results_data)
        filtered_scheduled = remove.filter(scheduled_data)


        for each in super_classifiers:
            if each["is_nominal"]:
                results = filtered_nominal_results
            else:
                results = filtered_results
            process_classifier(each["name"], each["options"], uuid_list, results, filtered_scheduled)

        # raise SystemExit(0)
        #
        # cls = train_classifier(filtered_results, classifier, [])
        # output_predictions(cls, filtered_scheduled, uuid_list)

    jvm.stop()
