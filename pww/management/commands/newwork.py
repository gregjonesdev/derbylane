from django.core.management.base import BaseCommand

from pww.utilities.ultraweka import create_model

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

    def handle(self, *args, **options):

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
        raise SystemExit(0)
        create_model(model_arff, classifier, options, filename)
