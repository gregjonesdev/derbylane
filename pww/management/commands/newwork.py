from django.core.management.base import BaseCommand
import datetime
from pww.utilities.ultraweka import create_model
from rawdat.models import Venue

from miner.utilities.constants import (
    focused_distances,
    csv_columns,
    )
from pww.models import Metric


class Command(BaseCommand):

    def get_options(self):
        jason_comment = '''
        weka.classifiers.functions.SMO -C 1.0 -L 0.001 -P 1.0E-12 -N 0 -V -1 -W 1 -K
        "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007"
        -calibrator "weka.classifiers.functions.Logistic -R 1.0E-8 -M -1 -num-decimal-places 4"
        '''

        return [
        "-C", "1.0", # The complexity constant C. (default 1)
        "-L", "0.001",
        "-P", "1.0E-12", # The epsilon for round-off error. (default 1.0e-12)
        "-N", "0", # Whether to 0=normalize/1=standardize/2=neither. (default 0=normalize)
        "-W", "1", # The random number seed. (default 1)
        "-V", "-1", # The number of folds for the internal cross-validation. (default -1, use training data)
        # Following line will be included in Kernel instantiation
        "-K", "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007",
        "-calibrator", "weka.classifiers.functions.Logistic -R 1.0E-8 -M -1 -num-decimal-places 4"
        ]


        # SMO Valid options are:
        #  -no-checks
        #   Turns off all checks - use with caution!
        #   Turning them off assumes that data is purely numeric, doesn't
        #   contain any missing values, and has a nominal class. Turning them
        #   off also means that no header information will be stored if the
        #   machine is linear. Finally, it also assumes that no instance has
        #   a weight equal to 0.
        #   (default: checks on)
        #
        #  -C <double>
        #   The complexity constant C. (default 1)
        #
        #  -N
        #   Whether to 0=normalize/1=standardize/2=neither. (default 0=normalize)
        #
        #  -L <double>
        #   The tolerance parameter. (default 1.0e-3)
        #
        #  -P <double>
        #   The epsilon for round-off error. (default 1.0e-12)
        #
        #  -M
        #   Fit calibration models to SVM outputs.
        #
        #  -V <double>
        #   The number of folds for the internal cross-validation. (default -1, use training data)
        #
        #  -W <double>
        #   The random number seed. (default 1)
        #
        #  -K <classname and parameters>
        #   The Kernel to use.
        #   (default: weka.classifiers.functions.supportVector.PolyKernel)
        #
        #  -calibrator <scheme specification>
        #   Full name of calibration model, followed by options.
        #   (default: "weka.classifiers.functions.Logistic")
        #
        #  -output-debug-info
        #   If set, classifier is run in debug mode and
        #   may output additional info to the console
        #
        #  -do-not-check-capabilities
        #   If set, classifier capabilities are not checked before classifier is built
        #   (use with caution).
        #
        #  -num-decimal-places
        #   The number of decimal places for the output of numbers in the model (default 2).
        #
        #
        #  Options specific to kernel weka.classifiers.functions.supportVector.PolyKernel:
        #
        #
        #  -E <num>
        #   The Exponent to use.
        #   (default: 1.0)
        #
        #  -L
        #   Use lower-order terms.
        #   (default: no)
        #
        #  -C <num>
        #   The size of the cache (a prime number), 0 for full cache and
        #   -1 to turn it off.
        #   (default: 250007)
        #
        #  -output-debug-info
        #   Enables debugging output (if available) to be printed.
        #   (default: off)
        #
        #  -no-checks
        #   Turns off all checks - use with caution!
        #   (default: checks on)
        #
        #
        #  Options specific to calibrator weka.classifiers.functions.Logistic:
        #
        #
        #  -C
        #   Use conjugate gradient descent rather than BFGS updates.
        #
        #  -R <ridge>
        #   Set the ridge in the log-likelihood.
        #
        #  -M <number>
        #   Set the maximum number of iterations (default -1, until convergence).
        #
        #  -output-debug-info
        #   If set, classifier is run in debug mode and
        #   may output additional info to the console
        #
        #  -do-not-check-capabilities
        #   If set, classifier capabilities are not checked before classifier is built
        #   (use with caution).
        #
        #  -num-decimal-places
        #   The number of decimal places for the output of numbers in the model (default 2).

    def create_arff(self, filename, metrics, is_nominal):
        scheduled_start = "2021-07-14"
        start_datetime = datetime.datetime.strptime(scheduled_start, "%Y-%m-%d").date()
        arff_file = open(filename, "w")
        arff_file.write("@relation Metric\n")

        arff_file = self.write_headers(arff_file, is_nominal)

        for metric in metrics:
            csv_metric = metric.build_csv_metric(start_datetime)
            if csv_metric:
                arff_file.writelines(csv_metric)

        return filename

    def write_headers(self, arff_file, is_nominal):
        for each in csv_columns:
            if is_nominal and each == "Fi":
                arff_file.write("@attribute {} nominal\n".format(each))
            elif each == "PID":
                arff_file.write("@attribute PID string\n")
                # csv_writer.writerow(["@attribute PID string"])
            elif each == "Se":
                arff_file.write("@attribute Se {M, F}\n")
                # csv_writer.writerow(["@attribute Se {M, F}"])
            else:
                # csv_writer.writerow(["@attribute {} numeric".format(each)])
                arff_file.write("@attribute {} numeric\n".format(each))

        arff_file.write("@data\n")
        return arff_file

    def handle(self, *args, **options):
        arff_directory = "arff"
        venue = Venue.objects.get(code="WD")
        venue_code = venue.code
        distance = focused_distances[venue_code][0]
        grade_name = "AA"
        print("{}_{}_{}".format(
            venue_code,
            distance,
            grade_name))
        metrics = Metric.objects.filter(
            participant__race__chart__program__venue=venue,
            participant__race__distance=distance,
            participant__race__grade__name=grade_name,
            participant__race__chart__program__date__lte="2021-09-14",
            final__isnull=False)
        print(len(metrics))


        race_key = "{}_{}_{}".format(venue_code, distance, grade_name)

        root_filename = "{}_smo".format(
            race_key)
        arff_filename = "{}/{}.arff".format(
            arff_directory,
            root_filename)
                    # print(arff_filename)
        is_nominal = False
        arff_file = self.create_arff(
            arff_filename,
            metrics,
            is_nominal)



        # Jasons comment



        # 10:40:57
        # Two AttributeSelectedClassifier lines with the following in the middle:
        # See weka.py build_scheduled_data
        # Thats on the evaluatuin side!
        comment = '''
        weka.classifiers.meta.AttributeSelectedClassifier
        -E "weka.attributeSelection.CfsSubsetEval -P 1 -E 1"
        -S "weka.attributeSelection.BestFirst" -D1 -N3"
        -W weka.classifiers.functions.SMO -- -C  1.0 -L
        '''


         # -E <attribute evaluator specification>
         #  Full class name of attribute evaluator, followed
         #  by its options.
         #  eg: "weka.attributeSelection.CfsSubsetEval -L"
         #  (default weka.attributeSelection.CfsSubsetEval)
         #
         # -S <search method specification>
         #  Full class name of search method, followed
         #  by its options.
         #  eg: "weka.attributeSelection.BestFirst -D 1"
         #  (default weka.attributeSelection.BestFirst)
         #
         # -D
         #  If set, classifier is run in debug mode and
         #  may output additional info to the console
         #
         # -W
         #  Full name of base classifier.
         #  (default: weka.classifiers.trees.J48)





        log = '''
        [base relation is now metric]
        [unsupervised Attribute remove R1]
        [numeric to nominal]
        [Base Relation is now Metric-weka.filters]
        [Started weka.classifiers.functions.SMO]
        '''

        print("hi")



        options = self.get_options()
        print(arff_file)
        print(options)
        raise SystemExit(0)
        create_model(arff_file, options, filename)
