
classifiers = {
    "smo": {
        "path": "weka.classifiers.functions.SMO",
        "is_nominal": True,
        "options": [
            "-L", "0.001",
            "-P", "1.0E-12",
            "-N", "0",
            "-W", "1",
            "-V", "10",
            "-K", "weka.classifiers.functions.supportVector.PolyKernel -E 1.0 -C 250007",
            "-calibrator", "weka.classifiers.functions.Logistic -R 1.0E-8 -M -1 -num-decimal-places 4"
        ],
    },
    "j48": {
        "path": "weka.classifiers.trees.J48",
        "is_nominal": True,
        "options": [],
    },
    "randomforest": {
        "is_nominal": True,
        "path": "weka.classifiers.trees.RandomForest",
        "options": [
            #  "-B", # Break ties randomly when several attributes look equally good.
            # "-U" # Allow unclassified instances.
        ],
    },
    "nbu": {
        "is_nominal": True,
        "path": "weka.classifiers.bayes.NaiveBayesUpdateable",
        "options": [],
    },
    "nb": {
        "path": "weka.classifiers.bayes.NaiveBayes",
        "options": [],
    },
    "zeror": {
        "path": "weka.classifiers.rules.ZeroR",
        "options": [],
    },
    "reptree": {
        "path": "weka.classifiers.trees.REPTree",
        "options": [],
    },
    # "simplek": {
    #     "classname": "weka.clusterers.SimpleKMeans",
    #     "options": [],
    # },
    "ll": {
        "path": "weka.classifiers.functions.LibLINEAR",
        "options": [],
    },
    "smoreg": {
        "path": "weka.classifiers.functions.SMOreg",
        "is_nominal": False,
        "options": [
        "-C", "1.0",
        "-N", "0",
        "-I", "weka.classifiers.functions.supportVector.RegSMOImproved",
        "-K", "weka.classifiers.functions.supportVector.RBFKernel",
        # RegSMOImproved Specific:
        # "-T", "0.001", (DEFAULT)
        # "-V", (DEFAULT)
        # "-P", "1.0E-12", (DEFAULT)
        # "-L", "0.001", (DEFAULT)
        # "-W", "1", (DEFAULT)
        # Using defualt K PolyKernel:
        # "-C", "250007", (DEFAULT)
        # Unknown:
        # "-G", "0.01"
        ],
    },
}
