

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

def split_position_lengths(entry):
    if entry:
        split_entry = entry.replace("-", " ").split()
        return split_entry
    return [None, None]


def get_final_and_lengths_behind(split_final):
    try:
        final = split_final[0]
        if len(split_final) > 1:
            lengths_behind = get_result_lengths_behind(split_final)
        else:
            lengths_behind = None
    except IndexError:
        final = None
        lengths_behind = None
    return [final, lengths_behind]

def get_positions(row):
    positions = []
    i = 2
    while i < 5:
        split_position = split_position_lengths(row[i].text)
        if len(split_position) > 0:
            positions.append(split_position[0])
        else:
            positions.append(None)
        i += 1
    return positions


def get_race_rows(all_tds, div_tds):
    race_rows = []
    for div_td in div_tds:
        race_rows.append(div_td.getparent().getparent())
    return race_rows

def parse_row(row, race):
    positions = get_positions(row)
    final_lengths = get_final_and_lengths_behind(
        split_position_lengths(row[5].text))
    final = final_lengths[0]
    lengths_behind = final_lengths[1]

def get_results(target_url, all_tds, race):
    div_tds = get_node_elements(target_url, '//td//div')
    race_rows = get_race_rows(all_tds, div_tds)
    for row in race_rows:
        if len(row) is 10:
            parse_row(row, race)

def check_for_results(race, page_data):
    td_count = len(page_data)
    print(td_count)
    if td_count > 50:
        print('process results')
        get_results(url, all_tds, race)
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
