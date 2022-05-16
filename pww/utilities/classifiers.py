
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
        "is_nominal": True,
        "path": "weka.classifiers.bayes.NaiveBayes",
        "options": [],
    },
    "zeror": {
        "is_nominal": True,
        "path": "weka.classifiers.rules.ZeroR",
        "options": [],
    },
    "reptree": {
        "is_nominal": True,
        "path": "weka.classifiers.trees.REPTree",
        "options": [],
    },
    "ll": {
        "is_nominal": True,
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


model_data = [
    {
        "start_date": "2019-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "SL",
        "grade_name": "A",
    },
    {
        "start_date": "2018-06-01",
        "end_date":	"2021-12-31",
        "venue_code": "SL",
        "grade_name": "A",
    },
    {
        "start_date": "2018-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "SL",
        "grade_name": "B",
    },
    {
        "start_date": "2021-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "WD",
        "grade_name": "C",
    },
    {
        "start_date": "2020-09-01",
        "end_date":	"2021-12-31",
        "venue_code": "WD",
        "grade_name": "C",
    },
    {
        "start_date": "2018-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "WD",
        "grade_name": "B",
    },
    {
        "start_date": "2018-12-01",
        "end_date":	"2021-12-31",
        "venue_code": "TS",
        "grade_name": "A",
    },
    {
        "start_date": "2021-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "TS",
        "grade_name": "B",
    },
    {
        "start_date": "2019-06-01",
        "end_date":	"2021-12-31",
        "venue_code": "TS",
        "grade_name": "C",
    },
    {
        "start_date": "2021-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "TS",
        "grade_name": "D",
    },
    {
        "start_date": "2020-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "TS",
        "grade_name": "D",
    },
    {
        "start_date": "2020-09-01",
        "end_date":	"2021-12-31",
        "venue_code": "SL",
        "grade_name": "B",
    },
    {
        "start_date": "2021-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "SL",
        "grade_name": "C",
    },
    {
        "start_date": "2020-06-01",
        "end_date":	"2021-12-31",
        "venue_code": "SL",
        "grade_name": "C",
    },
    {
        "start_date": "2020-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "SL",
        "grade_name": "C",
    },
    {
        "start_date": "2019-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "SL",
        "grade_name": "D",
    },
    {
        "start_date": "2018-06-01",
        "end_date":	"2021-12-31",
        "venue_code": "WD",
        "grade_name": "AA",
    },
    {
        "start_date": "2018-01-01",
        "end_date":	"2021-12-31",
        "venue_code": "WD",
        "grade_name": "AA",
    },
    {
        "start_date": "2017-06-01",
        "end_date":	"2021-12-31",
        "venue_code": "WD",
        "grade_name": "AA",
    },
    {
        "start_date": "2020-06-01",
        "end_date":	"2021-12-31",
        "venue_code": "WD",
        "grade_name": "A",
    },
]

reccomendations = {

    "TS_D_2021_01_01": [
        {
        "start": 4.62,
        "end": 4.69,
        "bet": "PS",
        },
    ],

    "SL_C_2021_01_01": [
        {
        "start": 4.19,
        "end": 4.25,
        "bet": "W",
        },
    ],
    "TS_D_2020_01_01": [
        {
        "start": 4.81,
        "end": 4.88,
        "bet": "W",
        },
    ],
    "SL_B_2020_09_01": [
        {
        "start": 4.06,
        "end": 4.12,
        "bet": "P",
        },
    ],
    "TS_B_2021_01_01": [
        {
        "start": 4.62,
        "end": 4.69,
        "bet": "WPS",
        },
    ],
    "SL_C_2020_06_01": [
        {
        "start": 4.12,
        "end": 4.19,
        "bet": "S",
        },
    ],
    "TS_A_2018_12_01": [
        {
        "start": 4.5,
        "end": 4.56,
        "bet": "WP",
        },
    ],
    "SL_C_2020_01_01": [
        {
        "start": 4.19,
        "end": 4.25,
        "bet": "P",
        },
    ],
    "WD_A_2020_06_01": [
        {
        "start": 4.06,
        "end": 4.12,
        "bet": "WPS",
        },
        {
        "start": 4.19,
        "end": 4.25,
        "bet": "W",
        },
    ],
    "WD_C_2021_01_01": [
        {
        "start": 4.0,
        "end": 4.06,
        "bet": "P",
        },
    ],
    "SL_A_2019_01_01": [
        {
        "start": 4.56,
        "end": 4.62,
        "bet": "P",
        },
    ],
    "WD_C_2020_09_01": [
        {
        "start": 4.5,
        "end": 4.56,
        "bet": "W",
        },
    ],
    "TS_C_2019_06_01": [
        {
        "start": 4.62,
        "end": 4.69,
        "bet": "WPS",
        },
    ],
    "SL_A_2018_06_01": [
        {
        "start": 4.56,
        "end": 4.62,
        "bet": "W",
        },
    ],
    "WD_AA_2018_06_01": [
        {
        "start": 4.56,
        "end": 4.62,
        "bet": "W",
        },
    ],
    "SL_D_2019_01_01": [
        {
        "start": 4.5,
        "end": 4.56,
        "bet": "WP",
        },
    ],
    "WD_AA_2018_01_01": [
        {
        "start": 4.06,
        "end": 4.12,
        "bet": "P",
        },
    ],
    "WD_AA_2017_06_01": [
        {
        "start": 5.12,
        "end": 5.19,
        "bet": "S",
        },
    ],
    "SL_B_2018_01_01": [
        {
        "start": 4.19,
        "end": 4.25,
        "bet": "W",
        },
    ],
    "WD_B_2018_01_01": [
        {
        "start": 4.19,
        "end": 4.25,
        "bet": "W",
        },
        {
        "start": 4.62,
        "end": 4.69,
        "bet": "PS",
        },
    ],
}
