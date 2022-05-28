from miner.utilities.common import get_attribute_elements, get_node_elements

from miner.utilities.comments import no_elements
from miner.utilities.models import get_race, get_grade, get_condition
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

def parse_race_setting(td):
    single_line_text = remove_line_breaks(td.text)
    untabbed_text = remove_tabs(single_line_text)
    unspaced_text = remove_extra_spaces(untabbed_text)
    return unspaced_text.split()

def save_race_settings(race, tds):
    race_setting_index = get_race_setting_index(race.number, tds)
    td = tds[race_setting_index]
    parsed_setting = parse_race_setting(td)
    try:
        race.grade = get_grade(parsed_setting[2])
        race.distance = get_race_distance(parsed_setting[3])
        # race.condition = get_condition(parsed_setting[4])
    except IndexError:
        print("Index Error:")
        print(parsed_setting)
    race.save()

def get_exotic_bet_list(tds):
    exotic_bet_list = []
    for td in tds:
        for each in td:
            text = each.text
            if text and "$2.00" in text:
                exotic_bet_list.append(text)
    return exotic_bet_list

def get_posts_index(split_text):
    for entry in split_text:
        if "/" in entry:
            return split_text.index(entry)

def get_payout(split_text):
    payout = split_text[-1]
    return float(
        payout.replace(
        "$", "").replace(
        ",", ""))

def get_exotic_name(split_text, posts_index):
    type_text = split_text[1:posts_index]
    if len(type_text) > 1:
        new_type = ""
        for each in type_text:
            new_type += "{} ".format(each)
        return new_type.strip()
    else:
        return type_text[0]

def get_posts_from_table(tds):
    print("get posts from table")

def get_posts_list(split_text, posts_index):
    posts_list = []
    posts = split_text[posts_index]
    for post in posts.split("/"):
        posts_list.append(int(post))
    return posts_list



def parse_exotic_bets(split_text, tds):
    payout = get_payout(split_text)
    posts_index =  get_posts_index(split_text)
    exotic_name = get_exotic_name(split_text, posts_index)
    #try
    posts_list = get_posts_list(split_text, posts_index)
    #except
    # get_posts_from_table(tds)
    # print(payout)
    # print(posts_list)
    # print(exotic_name)

def save_exotic_bets(race, tds):
    for exotic_bet_text in get_exotic_bet_list(tds):
        parse_exotic_bets(exotic_bet_text.split(), tds)

def get_race_setting_index(race_number, tds):
    for td in tds:
        if td.text:
            text = td.text.lower()
            if "race" in text and str(race_number) in text:
                return tds.index(td)


def save_race_results(race, tds):
    save_race_settings(race, tds)
    if len(tds) >= 105:
        save_exotic_bets(race, tds)
    else:
        print("TDS: {}".format(len(tds)))
        raise SystemExit(0)
