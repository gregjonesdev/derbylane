import re
from django.core.exceptions import ObjectDoesNotExist
from miner.utilities.urls import (
    build_entries_url,
    build_race_results_url,
    build_dog_results_url,
)
from rawdat.models import Weather
from miner.utilities.constants import (
    distance_converter,
    position_skips,
    chart_times,
    allowed_attempts,
    max_races_per_chart,
    art_skips,
    no_greyhound_names,
    raw_types,
    dogname_corrections,
    )

from rawdat.utilities.methods import get_date_from_ymd

from pww.utilities.metrics import build_race_metrics
from pww.models import Metric
from miner.utilities.models import (
    update_participant,
    save_race_info,
    get_participant,
    # create_single,
    get_dog,
    get_race,
    get_straightwager,
    get_grade,
    get_chart,
    get_program,
    create_exacta,
    create_quiniela,
    create_trifecta,
    create_superfecta,
)

from miner.utilities.weather import (
    build_weather_from_almanac,
)

from miner.utilities.common import (
    get_node_elements,
    get_attribute_elements,
    force_date
)

def split_position_lengths(entry):
    if entry:
        split_entry = entry.replace("-", " ").split()
        return split_entry
    return [None, None]


def get_result_lengths_behind(split_final):
    final = split_final[0]
    lengths = None
    if final.isnumeric() and int(final) > 1:
        if len(split_final) > 1:
            try:
                lengths = float(split_final[1])
            except ValueError:
                if int(final) > 6:
                    lengths = 30
    return lengths


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
    i = 1
    while i < 5:
        split_position = split_position_lengths(row[i].text)
        if len(split_position) > 0:
            positions.append(split_position[0])
        else:
            positions.append(None)
        i += 1
    return positions





def get_post_weight(dog_name, date):
    target_url = build_dog_results_url(dog_name)
    string_date = "{}".format(date)
    # entries = get_node_elements(target_url, '//td[@class="raceline"]')
    entries = get_attribute_elements(target_url, 'td', 'class', 'raceline')
    entries = get_node_elements(target_url, '//tr')
    for entry in entries:
        date = entry[0][0].text.strip().split()[0]
        if date == string_date:
            try:
                float_weight = float(entry[5].text.strip())
                if 20 < float_weight < 90:
                    return float_weight
            except:
                return None


def get_position(raw_position):
    if raw_position:
        raw_position = raw_position.strip()
        if raw_position:
            if isinstance(raw_position, str):
                for skip in position_skips:
                    if raw_position.find(skip) > -1:
                        if len(raw_position) < 2:
                            return None
                        else:
                            raw_position = raw_position.replace(skip, "")
            try:
                return int(raw_position)
            except:
                pass
        else:
            return None
    else:
        return None


def get_time(entry):
    if isinstance(entry, str):
        entry = entry.strip()
    if entry.upper() in art_skips:
        return None
    try:
        return float(entry)
    except ValueError:
        return None


def parse_row(row, race):
    pritn("parse row")
    # for each in row:
    #     print(each.text)
    positions = get_positions(row)
    final_lengths = get_final_and_lengths_behind(
        split_position_lengths(row[5].text))
    final = final_lengths[0]
    lengths_behind = final_lengths[1]
    name = row[0][0].text
    if name.upper() in dogname_corrections:
        name = dogname_corrections[name]
    dog = get_dog(name)
    participant = get_participant(race, dog)
    post_weight = get_post_weight(
        participant.dog.name,
        race.chart.program.date)
    # print(final)
    # print(post_weight)
    # print(lengths_behind)

    update_participant(
        participant,
        post_weight,
        get_position(positions[0]), #post
        get_position(row[1].text), # off
        get_position(positions[1]), # eighth
        get_position(positions[2]), # straight
        get_position(final),
        get_time(row[6].text),
        lengths_behind,
        row[9].text.strip())




def get_results(target_url, page_data, race):
    print(target_url)
    div_tds = get_node_elements(target_url, '//td//div')
    race_rows = get_race_rows(div_tds)
    for row in race_rows:
        if len(row) == 10:
            parse_row(row, race)


def get_race_rows(div_tds):
    race_rows = []
    for div_td in div_tds:
        race_rows.append(div_td.getparent().getparent())
    return race_rows


def process_combo_bets(race, target_url):
    # print("process combo bets")
    # for part in race.participant_set.all():
    #     print("{}: {}".format(part.post, part.dog.name))
    for each in get_node_elements(target_url, '//p'):
        if each.text:
            split_text = each.text.split()
            if len(split_text) > 0:
                cost = get_dollar_amount(split_text[0])
                if split_text[2].isalpha():
                    combo_name = get_combo_name("{} {}".format(
                        split_text[1],
                        split_text[2]))
                    posts_index = 3
                else:
                    combo_name = get_combo_name(split_text[1].upper())
                    posts_index = 2
                posts = split_text[posts_index].split("/")
                print(posts)
                payout = get_dollar_amount(split_text[-1])
                if payout and combo_name:
                    lower_combo_name = combo_name.lower()
                    if not "big" in lower_combo_name:
                        if lower_combo_name == "exacta":
                            create_exacta(race, posts, cost, payout)
                        elif "quin" in lower_combo_name:
                            create_quiniela(race, posts, cost, payout)
                        elif lower_combo_name == "trifecta":
                            create_trifecta(race, posts, cost, payout)
                        elif lower_combo_name == "superfecta":
                            create_superfecta(race, posts, cost, payout)


def get_dollar_amount(string):
    if string:
        stripped = string.strip()
        if stripped:
            try:
                return float(stripped.replace("$", "").replace(",", ""))
            except:
                print("get_dollar_amt: couldnt float {}".format(string))
                pass
    else:
        return 0.0



def get_combo_name(text):
    # print("---")
    # print(text)
    # print("---")
    if 'TRI SUPER' in text:
        return None
    elif 'DOUB' in text:
        return None
    elif 'PIC' in text:
        return None
    elif 'TWIN' in text:
        return None
    elif 'QU' in text:
        return "Quiniela"
    elif 'TRI' in text:
        return "Trifecta"
    elif 'SUPERF' in text:
        return "Superfecta"
    elif 'EX' in text:
        return "Exacta"

    else:
        return None


def process_dog_bets(race, page_data):
    finisher_indices = [16, 22, 28]
    for index in finisher_indices:
        if isinstance(page_data[index].text, str):
            name = page_data[index].text.strip()
            if name.lower().find("cet easi eli") > -1:
                name = "Cet Easy Eli"

                dog = get_dog(name)

                participant = get_participant(race, dog)
                if participant:
                    chart = race.chart
                    program = chart.program
                    process_straightwagers(
                        participant,
                        page_data[index+1].text,
                        page_data[index+2].text,
                        page_data[index+3].text)


def process_straightwagers(participant, win_amount, place_amount, show_amount):
    straight_wager = get_straightwager(participant)
    # print(win_amount)
    # print(place_amount)
    # print(show_amount)
    straight_wager = get_straightwager(participant)
    straight_wager.win = get_dollar_amount(win_amount)
    straight_wager.place = get_dollar_amount(place_amount)
    straight_wager.show = get_dollar_amount(show_amount)
    straight_wager.save()


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


def is_race_heading_cell(text):
        if len(text) > 0:
            first_lower = text[0].lower()
            if first_lower.find('race') == 0:
                if first_lower.find('raced') < 0:
                    if not re.search('[a-zA-Z]', text[1]):
                        return True


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
        if name and not name in no_greyhound_names:
            dog = get_dog(dognames[i])
            post_position = i + 1
            participant = get_participant(race, dog)
            if not participant.post:
                set_post(
                    participant,
                    post_position)
        i += 1


def scan_scheduled_charts(venue, program):
    for time in chart_times:
        number = 1
        failed_attempts = 0
        while failed_attempts <= allowed_attempts and number <= max_races_per_chart:
            program_date = force_date(program.date)
            entries_url = build_entries_url(
                venue.code,
                program_date.year,
                program_date.month,
                program_date.day,
                time,
                number)
            page_data = get_node_elements(entries_url, '//td')
            if len(page_data) > 20:
                chart = get_chart(program, time)
                race = get_race(chart, number)
                save_race_info(
                    race,
                    get_raw_setting(page_data))
                populate_race(
                    get_entries_dognames(entries_url),
                    race)
                if race.grade and race.grade.value:
                    build_race_metrics(race)

            else:
                failed_attempts += 1
            number += 1

def get_entries_dognames(url):
    dognames = []
    anchor_elements = get_node_elements(url, '//a')
    for each in anchor_elements:
        text = each.text
        if text:
            if not re.search('[0-9]', text) and not re.search('▼', text):
                dog_name = text.strip()
                if dog_name.upper() in dogname_corrections:
                    dog_name = dogname_corrections[dog_name]
                    if not dog_name in dognames:
                        dognames.append(dog_name)
    return dognames


def get_result_dognames(url):
    dognames = []
    elements = get_attribute_elements(
        url,
        'div',
        'style',
        "text-overflow:ellipsis;white-space:nowrap;width:5em;overflow:hidden;"
    )
    for element in elements:
        text = element.text
        if not re.search('[0-9]', text):
            dog_name = text.strip()
            if dog_name.upper() in dogname_corrections:
                dog_name = dogname_corrections[dog_name]
                if not dog_name in dognames:
                    dognames.append(dog_name)
    return dognames



def parse_results_url(results_url, race, page_data):
    build_weather_from_almanac(race.chart.program)
    save_race_info(
        race,
        get_raw_setting(page_data))
    # print(results_url)
    populate_race(
        get_result_dognames(results_url),
        race)
    get_results(results_url, page_data, race)
    build_race_metrics(race)

    if len(page_data) > 115:
        process_combo_bets(race, results_url)
        process_dog_bets(race, page_data)




def scan_history_charts(venue, year, month, day):
    for time in chart_times:
        number = 1
        failed_attempts = 0
        while failed_attempts <= allowed_attempts and number <= max_races_per_chart:
            results_url = build_race_results_url(
                venue.code,
                year,
                month,
                day,
                time,
                number)
            page_data = get_node_elements(results_url, '//td')
            if len(page_data) > 85:
                formatted_date = get_date_from_ymd(year, month, day)
                program = get_program(
                    venue,
                    formatted_date)
                build_weather_from_almanac(program)
                race = get_race(
                    get_chart(program, time),
                    number)
                parse_results_url(results_url, race, page_data)
            else:
                failed_attempts += 1
            number += 1
