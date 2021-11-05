from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):

        # Jasons comment

        # 10:40:57
        # Two AttributeSelectedClassifier lines with the following in the middle:
        comment = '''
        weka.classifiers.meta.AttributeSelectedClassifier
        -E "weka.attributeSelection.CfsSubsetEval -P 1 -E 1"
        -S "weka.attributeSelection.BestFirst" -D1 -N3"
        -W weka.classifiers.functions.SMO -- -C  1.0 -L
        '''




        log = '''
        [base relation is now metric]
        [unsupervised Attribute remove R1]
        [numeric to nominal]
        [Base Relation is now Metric-weka.filters]
        [Started weka.classifiers.functions.SMO]
        '''

        one_long_line = '''
        weka.classifiers.functions.SMO -C 1.0 -L 0.001 -P 1.0E-12 -N 0 -V -1 -W 1 -K "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007"
        -calibrator "weka.classifiers.functions.Logistic -R 1.0E-8 -M -1 -num-decimal-places 4"
        '''
