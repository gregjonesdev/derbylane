from miner.utilities.comments import success, no_elements
from miner.utilities.common import (
    get_attribute_elements,
    clean_race_setting,
    get_dog,
    get_node_elements,
    get_grade
)
from miner.utilities.constants import (
    bad_characters,
    art_skips,
    post_weight,
    position_skips,
    length_converter,
)
from miner.utilities.urls import build_dog_results_url
from miner.utilities.models import (
    get_race,
    get_condition,
    update_participant,
    get_participant,
    create_straight_bet,
    create_exacta,
    create_quinella,
    create_trifecta,
    create_superfecta)

def has_results(url):
    tds = get_node_elements(url, "//td")
    return len(tds) > 33

def process_url(url, race):
    if has_results(url):
        tds = get_node_elements(url, "//td")
        parsed_setting = get_parsed_results_race_setting(url)
        save_race_settings(race, parsed_setting)
        trs = get_node_elements(url, "//tr")
        update_race_condition(race, url)
        return save_race_results(race, tds, trs)
    return no_elements

def get_parsed_results_race_setting(url):
    td = get_attribute_elements(
        url,
        "td",
        "width",
        "90%")[1]
    return clean_race_setting(td)

def save_race_settings(race, parsed_setting):
    try:
        race.grade = get_grade(parsed_setting[2])
        race.distance = get_race_distance(parsed_setting[3])
    except IndexError:
        print("Index Error:")
        print(parsed_setting)
    race.save()

def get_race_distance(race_distance):
    return(int(race_distance))

def update_race_condition(race, url):
    parsed_setting = get_parsed_results_race_setting(url)
    try:
        race.condition = get_condition(parsed_setting[4])
    except IndexError:
        print("244 Index Error:")
        print(parsed_setting)
    race.save()

def save_race_results(race, tds, trs):
    parse_race_results(race, trs)
    save_straight_bets(race, trs)
    if has_exotic_bets(tds):
        save_exotic_bets(race, tds)
    else:
        print("TDS: {}".format(len(tds)))
        raise SystemExit(0)
    return success

def parse_race_results(race, trs):
    for row in get_participant_rows(trs):
        dog_name = parse_dog_name(row[0][0].text)
        post = parse_position(row[1].text)
        off = parse_position(row[2].text)
        eighth = parse_position(row[3].text)
        straight = parse_position(row[4].text)
        final_and_lengths = get_final_and_lengths(row[5].text)
        final = parse_position(final_and_lengths[0])
        lengths_behind = final_and_lengths[1]
        actual_running_time = get_running_time(row[6].text)

        # print(dog_name)
        # print(post)
        # print(off)
        # print(eighth)
        # print(straight)
        # print(final)
        # print(lengths_behind)
        # print(actual_running_time)

        post_weight = get_post_weight(
            dog_name,
            race.chart.program.date)
        comment = row[9].text.strip()
        dog = get_dog(dog_name)
        update_participant(
            get_participant(race, dog),
            post_weight,
            post,
            off,
            eighth,
            straight,
            final,
            actual_running_time,
            lengths_behind,
            comment)

def get_race_number(race_number):
    return(int(race_number))

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

def get_posts_from_race(exotic_name, race):
    if exotic_name == "SUPERFECTA":
        posts_required = 4
    elif exotic_name == "TRIFECTA":
        posts_required = 3
    else:
        posts_required = 2
    posts = []
    i = 1
    while i <= posts_required:
        for participant in race.participant_set.all():
            if participant.final == i:
                posts.append(participant.post)
        i += 1
    return posts

def get_posts_list(split_text, posts_index):
    posts_list = []
    posts = split_text[posts_index]
    for post in posts.split("/"):
        posts_list.append(int(post))
    return posts_list

def parse_dog_name(raw_name):
    return raw_name.strip().upper()

def remove_bad_characters(string):
    if string:
        for character in bad_characters:
            string = string.replace(character, "")
    return string


def parse_position(raw_position):
    clean_position = remove_bad_characters(raw_position)
    if clean_position:
        if not clean_position in position_skips:
            return int(clean_position[0])

def get_final_and_lengths(text):
    split_text = text.split("-")
    final = None
    lengths_behind = None
    final = split_text[0]
    if not final in position_skips:
        if int(final) == 1:
            lengths_behind = 0
        elif len(split_text) > 1:
            lengths_behind = split_text[1]
            if lengths_behind in length_converter.keys():
                lengths_behind = length_converter[lengths_behind]
    return [final, lengths_behind]

def get_running_time(raw_time):
    if not raw_time.strip().upper() in art_skips:
        clean_time = remove_bad_characters(raw_time)
        return float(clean_time)

def get_post_weight(dog_name, date):
    target_url = build_dog_results_url(dog_name)
    string_date = "{}".format(date)
    entries = get_node_elements(target_url, '//tr')
    for entry in entries:
        date = entry[0][0].text.strip().split()[0]
        if date == string_date:
            try:
                float_weight = float(entry[5].text.strip())
                if post_weight["min"] < float_weight < post_weight["max"]:
                    return float_weight
            except:
                return None

def get_participant_rows(trs):
    participant_rows = []
    for tr in trs:
        if len(tr) == 10:
            participant_rows.append(tr)
    return participant_rows


def parse_exotic_bet(race, split_text, tds):
    payout = get_payout(split_text)
    posts_index =  get_posts_index(split_text)
    exotic_name = get_exotic_name(split_text, posts_index)
    try:
        posts_list = get_posts_list(split_text, posts_index)
    except:
        posts_list = get_posts_from_race(exotic_name, race)
    return [exotic_name, posts_list, payout]

def save_exotic_bets(race, tds):
    for exotic_bet_text in get_exotic_bet_list(tds):
        exotic_bet_data = parse_exotic_bet(
            race,
            exotic_bet_text.split(),
            tds)
        exotic_name = exotic_bet_data[0]
        if exotic_name == "TRIFECTA":
            create_trifecta(race, exotic_bet_data[1], exotic_bet_data[2])
        elif exotic_name == "SUPERFECTA":
            create_superfecta(race, exotic_bet_data[1], exotic_bet_data[2])
        elif exotic_name == "QUINELLA":
            create_quinella(race, exotic_bet_data[1], exotic_bet_data[2])
        elif exotic_name == "EXACTA":
            create_exacta(race, exotic_bet_data[1], exotic_bet_data[2])

def get_race_setting_index(race_number, tds):
    for td in tds:
        if td.text:
            text = td.text.lower()
            if "race" in text and str(race_number) in text:
                return tds.index(td)


def get_straight_bet_rows(trs):
    straight_bet_rows = []
    for tr in trs:
        if is_straight_bet_row(tr):
            straight_bet_rows.append(tr)
    return straight_bet_rows[1:]

def is_straight_bet_row(tr):
    return len(tr)==3 and td_has_text(tr[0])

def td_has_text(td):
    return td.text and td.text.strip()

def get_parsed_bet_row(row):
    parsed_row = []
    for td in row:
        if td.text:
            stripped_text = td.text.strip()
            parsed_row.append(stripped_text if stripped_text else 0)
    return parsed_row

def save_straight_bets(race, trs):
    for row in get_straight_bet_rows(trs):
        parsed_row = get_parsed_bet_row(row)
        dog = get_dog(parsed_row[0])
        participant = get_participant(race, dog)
        create_straight_bet(
            participant,
            "W",
            parsed_row[1])
        create_straight_bet(
            participant,
            "P",
            parsed_row[2])
        create_straight_bet(
            participant,
            "S",
            parsed_row[3])





def has_exotic_bets(tds):
    return len(tds) >= 96
