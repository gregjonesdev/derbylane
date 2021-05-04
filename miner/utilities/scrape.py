
from lxml import html

from miner.utilities.urls import (
    results_url,
)

from miner.utilities.constants import distance_converter

from rawdat.utilities.methods import (
    get_program,
    get_chart,
    get_race
)

from rawdat.utilities.constants import (
    chart_times,
    allowed_attempts,
    max_races_per_chart,
)

from miner.utilities.models import (
    update_participant,
    save_sex,
    save_post_weight,
    save_race_info,
    get_participant,
    create_combination,
    create_single,
    get_dog,
    get_bettype,
    get_grade,
)

from miner.utilities.common import get_node_elements


def check_for_results(race, page_data):
    td_count = len(page_data)
    print(td_count)
    if td_count > 50:
        print('process results')
        if td_count > 110:
            print('process bets')

def get_race_heading(target_url):
        for td in get_node_elements(target_url, '//td'):
            try:
                formatted_text = format_text(td.text)
                if is_race_heading_cell(formatted_text):
                    return formatted_text
            except AttributeError:
                pass

def format_text(text):
    return text.replace("\n", "").replace("  ", "").strip().split()

def build_race(venue, year, month, day, time, number):
    program = get_program(
        venue,
        year,
        month,
        day)
    chart = get_chart(program, time)
    return get_race(chart, number)

def is_race_heading_cell(text):
        if len(text) > 0:
            first_lower = text[0].lower()
            if first_lower.find('race') is 0:
                if first_lower.find('raced') < 0:
                    if not re.search('[a-zA-Z]', text[1]):
                        return True

def process_race(race, page_data, anchor_elements):
    save_race_info(
        race,
        get_raw_setting(page_data))
    populate_race(
        get_dognames(anchor_elements),
        race)

def get_dognames(table):
        dognames = []
        for item in table:
            if item.text:
                if not re.search('[0-9]', item.text):
                    if not re.search('▼', item.text):
                        dognames.append(item.text.strip())
        return dognames

def get_raw_setting(tds):
    for td in tds:
        try:
            if td.text:
                text = td.text
                if "race" in text.lower() and re.search('[0-9]', text):
                    return text.strip().replace("\n","").replace("\t", "").split()
        except UnicodeDecodeError:
            pass

def set_post(participant, post_position):
        if post_position:
            participant.post = post_position
            participant.save()


def populate_race(dognames, race):
        i = 0
        for name in dognames:
            if not name in no_greyhound_names:
                dog = get_dog(dognames[i])
                post_position = i + 1
                participant = get_participant(race, dog)
                set_post(
                    participant,
                    post_position)
            i += 1

def save_race_info(race, raw_setting):
    print(raw_setting)
    if raw_setting:
        for item in raw_setting[:3]:
            if item.upper() in race_grades:
                race.grade = get_grade(item)
        for item in raw_setting:
            if item in distance_converter:
                item = distance_converter[item]
            try:
                item = int(item)
                if 100 < item < 900:
                    distance = int(item)
                    race.distance = distance
            except:
                pass
        for item in raw_setting[3:]:
            if item.upper() in race_conditions:
                race.condition = item.upper()
        race.save()

def scan_chart_times(venue, year, month, day):
    for time in chart_times:
        number = 1
        failed_attempts = 0
        while failed_attempts <= allowed_attempts and number <= max_races_per_chart:
            target_url = build_results_url(
                venue.code,
                year,
                month,
                day,
                time,
                number)
            print(target_url)
            page_data = get_node_elements(target_url, '//td')
            if has_race(page_data):
                print("has race data")
                race = build_race(venue, year, month, day, time, number)
                anchor_elements = get_node_elements(target_url, '//a')
                process_race(race, page_data, anchor_elements)
                check_for_results(race, page_data)
            else:
                failed_attempts += 1
            number += 1

def build_results_url(venue_code, year, month, day, time, race_number):
    return "{}G{}${}{}{}{}{}".format(
        results_url,
        venue_code,
        year,
        str(month).zfill(2),
        str(day).zfill(2),
        time,
        str(race_number).zfill(2))



def has_race(page_data):
    td_count = len(page_data)
    if td_count > 20:
        return True

def save_race_data(url):
    print("save_race_data")
    print(url)
