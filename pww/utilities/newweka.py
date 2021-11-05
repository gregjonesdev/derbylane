import weka.core.jvm as jvm
import weka.core.converters as conv

from weka.classifiers import Classifier, Evaluation
from weka.core.classes import Random
from weka.core.dataset import Instances
from weka.core.packages import install_missing_packages, LATEST
from weka.filters import Filter

def evaluate_all(arff_list, venue_code, grade_name):
    start_jvm()
    analysis_file = create_analysis_file(venue_code, grade_name)
    for arff_file in arff_list:
        evaluate_single(arff_file, analysis_file)
    analysis_file.close()
    jvm.stop()

def create_analysis_file(venue_code, grade_name):
    return open("prediction_analysis_{}_{}.txt".format(
        venue_code,
        grade_name), "w")

def evaluate_single(arff_file, analysis_file):
    race_key = arff_file.replace("arff/", "").replace(".arff", "")
    scheduled_data = build_scheduled_data(arff_file)
    # model_names = ["libsvm", "J48_C0_75"]
    model_names = ['smo']
    evaluate(arff_file, analysis_file, scheduled_data, model_names)

def get_race_key(arff_file):
    return arff_file.replace("arff/", "").replace(".arff", "")

def evaluate():
    print("here")


def example(data):
    print("example")

    classifier = Classifier(classname="weka.classifiers.trees.J48")

    # randomize data
    folds = 10
    seed = 1
    rand_data = randomize_data(data, folds, seed)

    # perform cross-validation and add predictions
    predicted_data = None
    evaluation = Evaluation(rand_data)
    for i in range(folds):
        train = rand_data.train_cv(folds, i)
        # the above code is used by the StratifiedRemoveFolds filter,
        # the following code is used by the Explorer/Experimenter
        # train = rand_data.train_cv(folds, i, rnd)
        test = rand_data.test_cv(folds, i)

        # build and evaluate classifier
        cls = Classifier.make_copy(classifier)
        cls.build_classifier(train)
        evaluation.test_model(cls, test)

        # add predictions
        addcls = Filter(
            classname="weka.filters.supervised.attribute.AddClassification",
            options=["-classification", "-distribution", "-error"])
        # setting the java object directory avoids issues with correct quoting in option array
        addcls.set_property("classifier", Classifier.make_copy(classifier))
        addcls.inputformat(train)
        addcls.filter(train)  # trains the classifier
        pred = addcls.filter(test)
        if predicted_data is None:
            predicted_data = Instances.template_instances(pred, 0)
        for n in range(pred.num_instances):
            predicted_data.add_instance(pred.get_instance(n))

    print("")
    print("=== Setup ===")
    print("Classifier: " + classifier.to_commandline())
    print("Dataset: " + data.relationname)
    print("Folds: " + str(folds))
    print("Seed: " + str(seed))
    print("")
    print(evaluation.summary("=== " + str(folds) + " -fold Cross-Validation ==="))
    print("")
    print(predicted_data)

def randomize_data(data, folds, seed):

    rnd = Random(seed)
    rand_data = Instances.copy_instances(data)
    rand_data.randomize(rnd)
    if rand_data.class_attribute.is_nominal:
        rand_data.stratify(folds)
    return rand_data



def build_scheduled_data(arff_data):
    loader = conv.Loader(classname="weka.core.converters.ArffLoader")
    loaded_data = loader.load_file(arff_data)
    anonymous_data = remove_uuid(loaded_data)
    scheduled_data = nominalize(anonymous_data)
    scheduled_data.class_is_last()

    # print(scheduled_data)
    print("11-06 FORWARD PROGRESS")
    # New
    # example(scheduled_data)
    search = ASSearch(classname="weka.attributeSelection.BestFirst", options=["-D", "1", "-N", "3"])
    evaluator = ASEvaluation(classname="weka.attributeSelection.CfsSubsetEval", options=["-P", "1", "-E", "1"])

    "weka.attributeSelection.WrapperSubsetEval -B"

    attsel = AttributeSelection()
    attsel.search(search)
    attsel.evaluator(evaluator)
    attsel.select_attributes(scheduled_data)


    print("# attributes: " + str(attsel.number_attributes_selected))
    print("attributes: " + str(attsel.selected_attributes))
    print("result string:\n" + attsel.results_string)
    raise SystemExit(0)
    return scheduled_data


def remove_uuid(data):
    remove = Filter(
        classname="weka.filters.unsupervised.attribute.Remove",
        options=["-R", "first"])
    remove.inputformat(data)
    return remove.filter(data)

def nominalize(data):
    nominalize = Filter(
        classname="weka.filters.unsupervised.attribute.NumericToNominal",
        options=["-R", "19"])
    nominalize.inputformat(data)
    return nominalize.filter(data)


def start_jvm():
    jvm.start(packages=True, max_heap_size="6048m")
    install_missing_packages([
        ('LibSVM', LATEST),
        ('LibLINEAR', LATEST)])
