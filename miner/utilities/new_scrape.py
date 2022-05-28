from miner.utilities.common import get_attribute_elements, get_node_elements
from rawdat.models import Grade, Condition
from miner.utilities.comments import no_elements
from miner.utilities.models import get_race
from django.core.exceptions import ObjectDoesNotExist

def remove_line_breaks(text):
    return text.replace("\n", "")

def remove_tabs(text):
    return text.replace("\t", "")

def remove_extra_spaces(text):
    return text.replace("  ", " ")

def get_race_number(race_number):
    return(int(race_number))

def get_race_distance(race_distance):
    return(int(race_distance))

def get_race_grade(race_grade):
    try:
        grade = Grade.objects.get(name=race_grade)
    except ObjectDoesNotExist:
        grade = Grade(
            name=race_grade
        )
        grade.set_fields_to_base()
        grade.save()
    return grade

def get_race_condition(race_condition):
    try:
        condition = Condition.objects.get(name=race_condition)
    except ObjectDoesNotExist:
        condition = Condition(
            name=race_condition
        )
        condition.set_fields_to_base()
        condition.save()
    return condition

def parse_race_setting(td):
    single_line_text = remove_line_breaks(td.text)
    untabbed_text = remove_tabs(single_line_text)
    unspaced_text = remove_extra_spaces(untabbed_text)
    return unspaced_text.split()

def save_race_settings(race, td):
    parsed_setting = parse_race_setting(td)
    try:
        race.grade = get_race_grade(parsed_setting[2])
        race.distance = get_race_distance(parsed_setting[3])
        race.condition = get_race_condition(parsed_setting[4])
    except IndexError:
        print("Index Error:")
        print(parsed_setting)
    race.save()

def get_exotic_bet_list(tds):
    exotic_bet_list = []
    for td in tds:
        if len(td) == 3:
            for each in td:
                exotic_bet_list.append(each.text)
    return exotic_bet_list


def save_exotic_bets(race, tds):

    exotic_bet_list = get_exotic_bet_list(tds)
    print(race)
    for exotic_bet in exotic_bet_list:
        print(exotic_bet)
    raise SystemExit(0)


def save_race_results(race, tds):
    save_race_settings(race, tds[4])
    if len(tds) >= 105:
        save_exotic_bets(race, tds)
    else:
        print("TDS: {}".format(len(tds)))
        raise SystemExit(0)
