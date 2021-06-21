import re
from django.core.exceptions import ObjectDoesNotExist
from miner.utilities.urls import (
    build_entries_url,
    build_race_results_url,
    build_dog_results_url,
)
from rawdat.models import Weather, Grade
from miner.utilities.constants import (
    distance_converter,
    position_skips,
    race_conditions,
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
    print("positions")
    print(positions)
    raise SystemExit(0)
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
    # for each in row:
    #     print(each.text)
    positions = get_positions(row)
    final_lengths = get_final_and_lengths_behind(
        split_position_lengths(row[5].text))
    final = final_lengths[0]
    lengths_behind = final_lengths[1]
    name = row[0][0].text
    upper_name = name.upper()
    if upper_name in dogname_corrections:
        upper_name = dogname_corrections[upper_name]
    dog = get_dog(upper_name)
    participant = get_participant(race, dog)
    post_weight = get_post_weight(
        participant.dog.name,
        race.chart.program.date)
    # print(final)
    # print(post_weight)
    # print(lengths_behind)

    return {
        "post_weight": None,
        "positions": positions
    }

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

# get_positions
# get_final_and_lengths_behind
# get_participant
# get_post_weight
# get_time
# get_comment
#
# get participant data
# update_participant

# save participant data vs print participant data

def get_results(target_url, page_data, race):
    print(target_url)
    div_tds = get_node_elements(target_url, '//td//div')
    race_rows = get_race_rows(target_url)
    for row in race_rows:
        if len(row) == 10:
            # print("race: {}".format(race.uuid))
            parse_row(row, race)


def get_rows_of_length(page_rows, length):
    target_rows = []
    for row in page_rows:
        if len(row) == length:
            target_rows.append(row)
    return target_rows


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
    text = text.upper()
    if 'BIG' in text:
        return None
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
                upper_name = dog_name.upper()
                if upper_name in dogname_corrections:
                    upper_name = dogname_corrections[upper_name]
                if not upper_name in dognames:
                    dognames.append(upper_name)
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
            upper_name = dog_name.upper()
            if upper_name in dogname_corrections:
                upper_name = dogname_corrections[upper_name]
            if not upper_name in dognames:
                dognames.append(upper_name)
    return dognames



def parse_results_url(results_url, race, page_data):
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

def get_exotic_bets(results_url):
    focused_bets = ["EXACTA", "QUINELLA", "TRIFECTA", "SUPERFECTA"]
    exotic_bets = []
    exotic_ps = get_node_elements(results_url, '//p')
    for each in exotic_ps:
        if len(each.text) > 1:
            split_data = each.text.split()
            exotic_name = ' '.join(split_data[1:-3]).upper()
            if exotic_name in focused_bets:
                exotic_bets.append({
                    "name": exotic_name,
                    "posts": split_data[-3].split("/"),
                    "payout": float(split_data[-1].replace("$", "").replace(",", ""))
                })
    return exotic_bets


def get_race_setting(tds):
    for td in tds:
        try:
            if td.text:
                text = td.text
                if "race" in text.lower() and re.search('[0-9]', text):
                    return text.strip().replace("\n","").replace("\t", "").split()
        except UnicodeDecodeError:
            pass

def is_grade(grade):
    return Grade.objects.filter(name=grade.upper()).exists()

def get_race_setting(raw_setting):
    setting = {
        "grade": None,
        "distance": None,
        "condition": None,
    }
    for item in raw_setting[:3]:
        if is_grade(item):
            setting["grade"] = get_grade(item)
    for item in raw_setting:
        if item in distance_converter:
            item = distance_converter[item]
        try:
            item = int(item)
            if 100 < item < 900:
                setting["distance"] = int(item)
        except:
            pass
    for item in raw_setting[3:]:
        if item.upper() in race_conditions:
            setting["condition"] = item.upper()
    return setting

def print_exotic_bets(exotic_bets):
    print("\nExotic Wagers:")
    for exotic_bet in exotic_bets:
        string = "{}\t"
        if len(exotic_bet["name"]) < 8:
            string += "\t"
        string += "{}\t"
        if len(exotic_bet["posts"]) < 4:
            string += "\t"
        string += "\t{}"
        print(string.format(
            exotic_bet["name"],
            exotic_bet["posts"],
            exotic_bet["payout"]
        ))
    print("\n")

def print_race_setting(raw_setting, race_number, race_setting):
    print("Raw Setting: {}\n".format(raw_setting))
    print("Race {}".format(race_number))
    print("Grade: {}".format(race_setting["grade"].name))
    print("Distance: {}".format(race_setting["distance"]))
    print("Condition: {}".format(race_setting["condition"]))

def get_race_data(race_rows):
    race_data = []

    for row in race_rows:
        race_data.append({
            "dogname": row[0][0].text,
            "post": row[1].text,
            "off": split_position_lengths(row[2].text)[0],
            "eighth": split_position_lengths(row[3].text)[0],
            "straight": split_position_lengths(row[4].text)[0],
            "final": split_position_lengths(row[5].text)[0],
            "lengths_behind": split_position_lengths(row[5].text)[1],
            "actual_running_time": row[6].text,
            "comment": row[9].text
        })
    return race_data

def print_race_data(race_data):
    string = "{}\t{}\t{}\t{}\t{}\t{}-{}\t{}\t{}"
    for each in race_data:
        print(string.format(
            each["dogname"][:15],
            each["post"],
            each["off"],
            each["eighth"],
            each["straight"],
            each["final"],
            each["lengths_behind"],
            each["actual_running_time"],
            each["comment"]
        ))

def print_single_bets(bet_rows):
    print("\nSingle Wagers:")
    i = 1
    print("Runner\t\tWin\t\tPlace\t\tShow")
    while i <= 3:
        current_row = bet_rows[i]
        print("{}\t\t{}\t\t{}\t\t{}".format(
            current_row[1].text.strip()[:5],
            current_row[2].text.strip(),
            current_row[3].text.strip(),
            current_row[4].text.strip()
            ))
        i += 1

def single_url_test(results_url, chart):
    print("\n{}\n".format(results_url))
    tds = get_node_elements(results_url, '//td')
    raw_setting = get_raw_setting(tds)
    race_setting = get_race_setting(raw_setting)
    race_number = results_url[-2:]

    if len(tds) > 20:
        page_rows = get_node_elements(results_url, '//tr')
        race_rows = get_rows_of_length(page_rows, 10)
        bet_rows = get_rows_of_length(page_rows, 5)
        exotic_bets = get_exotic_bets(results_url)
        race_data = get_race_data(race_rows)

        if chart:
            print("proceed to save race data")
            race = get_race(chart, race_number)
            new_save_race_info(race, race_setting)
            # save single bets(race,
            # save combo bets(race,
            # save race data(race,
            # build metric(race,
        else:
            print_race_setting(raw_setting, race_number, race_setting)
            print_single_bets(bet_rows)
            print_exotic_bets(exotic_bets)
            print_race_data(race_data)

def new_save_race_info(race, race_setting):
    print("new")
    race.condition = race_setting['condition']
    race.grade = race_setting['grade']
    race.distance = race_setting['distance']
    race.save()


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
                build_weather_from_almanac(race.chart.program)
                parse_results_url(results_url, race, page_data)
            else:
                failed_attempts += 1
            number += 1
