from miner.utilities.common import get_attribute_elements, get_node_elements
from miner.utilities.constants import bad_characters, art_skips
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

def parse_dog_name(raw_name):
    return raw_name.strip().upper()

def remove_bad_characters(string):
    for character in bad_characters:
        string = string.replace(character, "")
    return string


def parse_position(raw_position):
    clean_position = remove_bad_characters(raw_position)
    if clean_position:
        return int(clean_position[0])

def get_final_and_lengths(text):
    split_text = text.split("-")
    final = split_text[0]
    if int(final) == 1:
        lengths_behind = 0
    else:
        lengths_behind = split_text[1]
    return [final, lengths_behind]

def get_running_time(raw_time):
    clean_time = remove_bad_characters(raw_time)
    return float(clean_time[0])


def parse_exotic_bets(split_text, tds):
    print("parse exotic")
    payout = get_payout(split_text)
    posts_index =  get_posts_index(split_text)
    exotic_name = get_exotic_name(split_text, posts_index)
    #try
    posts_list = get_posts_list(split_text, posts_index)
    #except
    # get_posts_from_table(tds)
    index = 36

    while index <= 106:
        dog_name = parse_dog_name(tds[index][0].text)
        print(dog_name)
        post = parse_position(tds[index + 1].text)
        print(post)
        off = parse_position(tds[index + 2].text)
        print(off)
        eighth = parse_position(tds[index + 3].text)
        print(eighth)
        straight = parse_position(tds[index + 4].text)
        print(straight)
        final_and_lengths = get_final_and_lengths(tds[index + 5].text)
        final = parse_position(final_and_lengths[0])
        print(final)
        lengths_behind = float(final_and_lengths[1])
        print(lengths_behind)
        actual_running_time = get_running_time(tds[index + 6].text)
        print(actual_running_time)
        index += 10


    # for td in tds:
    #     if len(td) > 0 and td[0].text:
    #         print(len(td[0].text))
    #         print("{}: {}".format(tds.index(td), td.text))
    raise SystemExit(0)
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
    if len(tds) >= 106:
        save_exotic_bets(race, tds)
    else:
        print("TDS: {}".format(len(tds)))
        raise SystemExit(0)
