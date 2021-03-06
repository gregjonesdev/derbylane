distance_converter = {
    "5-16": 550,
    "3-16": 330,
    "3-8": 660,
    "1-4": 440,
    "4-16": 440,
    "9-16": 990,
}

bad_characters = [
    u'\xa0',
    '&nbsp',
]

csv_columns = [
    "PID",
    "SFT",
    "W",
    "P",
    "S",
    "B",
    "E",
    "St",
    "F",
    "G",
    "T7",
    "T3",
    "U",
    "A",
    # "Se",
    # "LB",
    "PF",
    # "TF",
    # "RHF",
    "Fi",
]
focused_bets = ["EXACTA", "QUINELLA", "TRIFECTA", "SUPERFECTA"]
race_conditions = [
 "F",
 "G",
 "L",
 "M",
 "S",
 "W"
]

post_weight = {
    "min": 20,
    "max": 99,
}


dogname_corrections = {
    "CET EASI ELI": "CET EASY ELI"
}

cost = 2.0
raw_types = ["WIN", "PLACE", "SHOW"]
grade_skips = ["--"]
zero_lengths = []
max_lengths = []

#Distances under a length are recorded as follows: Nose = 0.05 of a length,
#Short head = 0.1 of a length, head = 0.2 of a length, neck = 0.3 of a length,
#half a length = 0.5 of a length, three-quarters of a length = 0.75 of a length.
length_converter = {
    "nk": 0.3,
    "neck": 0.3,
    "head": 0.2,
    "hd": 0.2,
    "ns": 0,
}
position_skips = ['.', '-', 'S', 'f', 'X', 'x', '0', 'O', 'N', '0', '+', 'D', '\xa0X']
art_skips = ['.', '-', 'F', 'X', '0', '+', 'D', 'OOP', 'DNF', '\xa0DNF']
no_greyhound_names = ["NO+GREYHOUND", "NO GREYHOUND", "*", "[EMAIL PROTECTED]", "Cet Easi Eli"]
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
chart_times = [
 "A",
 "E",
 "L",
 "T",
 # "S",
 "M",
 # "N",
 # "X",
 # "Z"
]

models_directory = "../../../allmodels"
packages_directory = "../../../packages"

c_data = {
    "j48": {
        "c_start": 0.01,
        "c_stop": 0.49,
        "interval": 0.01,
    },
    "smo": {
        "c_start": 0,
        "c_stop": 8,
        "interval": 0.1,
    },
}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



allowed_attempts = 3
max_races_per_chart = 30

days_of_week = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

focused_distances = {
    "SL": [583],
    "CA": [546],
    "TS": [550],
    "WD": [548],
    # "IG": [550, 330]
}

betting_venues = ["WD", "TS", "SL"]

focused_grades = {
    "SL": ["A", "B", "C", "D"],
    # "CA": ["A", "B", "C", "D"],
    "TS": ["A", "B", "C", "D"],
    "WD": ["AA", "A", "B", "C"],
    # "IG": ["A", "B", "C", "D"]
}

venue_distances = {
"SL": [660, 583, 334, 703, 820],
"CA": [546, 690 ],
"IG": [550, 330],
"TS": [550, 677, 330],
"WD": [330, 548, 678],
}
