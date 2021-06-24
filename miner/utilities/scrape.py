import re
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from miner.utilities.urls import (
    build_entries_url,
    build_race_results_url,
    build_dog_results_url,
)
from rawdat.models import Weather, Grade, Straight_Wager
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
    cost,
    focused_bets
    )

from rawdat.utilities.methods import get_date_from_ymd

from pww.utilities.metrics import build_race_metrics
from pww.models import Metric
from miner.utilities.models import (
    update_participant,
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


def get_rows_of_length(page_rows, length):
    target_rows = []
    for row in page_rows:
        if len(row) == length:
            target_rows.append(row)
    return target_rows


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
                raw_setting = get_raw_setting(page_data)
                if raw_setting:
                    save_race_info(
                        race,
                        get_race_setting(raw_setting))

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


def get_exotic_bets(results_url):
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


def is_grade(grade):
    return Grade.objects.filter(name=grade.upper()).exists()

def get_race_setting(raw_setting):
    print("Raw setting: {}".format(raw_setting))
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
    print("Race {}".format(race_number))
    if race_setting:
        print("Grade: {}".format(race_setting["grade"].name))
        print("Distance: {}".format(race_setting["distance"]))
        print("Condition: {}".format(race_setting["condition"]))

def get_actual_running_time(text):
    if text.strip() not in art_skips:
        return text


def get_race_data(race_rows):
    race_data = []
    posts = []
    for row in race_rows:
        split_final = split_position_lengths(row[5].text)
        final_and_lengths = get_final_and_lengths_behind(split_final)
        if final_and_lengths[0] in position_skips:
            final = None
        else:
            final = final_and_lengths[0]
        current_post = row[1].text
        if not current_post in posts:
            posts.append(current_post)
            race_data.append({
                "dogname": row[0][0].text,
                "post": row[1].text,
                "off": split_position_lengths(row[2].text)[0],
                "eighth": split_position_lengths(row[3].text)[0],
                "straight": split_position_lengths(row[4].text)[0],
                "final": final,
                "lengths_behind": final_and_lengths[1],
                "actual_running_time": get_actual_running_time(row[6].text),
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

def print_single_bets(single_bets):
    print("\nSingle Wagers:")
    if single_bets:
        print("Runner\t\tWin\t\tPlace\t\tShow")
        for bet in single_bets:
            print("{}\t\t{}\t\t{}\t\t{}".format(
                bet["dog"].name[:5],
                bet["win"],
                bet["place"],
                bet["show"]
                ))
    else:
        print("None")

def get_single_bets(bet_rows):
    single_bets = []

    i = 1
    while i < len(bet_rows):
        current_row = bet_rows[i]
        dogname = current_row[1].text.strip().lower()
        print(dogname)
        if dogname in dogname_corrections:
            dogname = dogname_corrections[dogname]
        single_bets.append({
            "dog": get_dog(dogname),
            "win": get_dollar_amount(current_row[2].text),
            "place": get_dollar_amount(current_row[3].text),
            "show": get_dollar_amount(current_row[4].text)
        })
        i += 1
    return single_bets

def save_single_bets(race, single_bets):
    print("save single bets")
    for each in single_bets:
        # print(each)
        participant = get_participant(
            race,
            each["dog"])
        print(participant)
        try:
            straightwager = Straight_Wager.objects.get(
                participant=participant
            )
        except ObjectDoesNotExist:
            new_straightwager = Straight_Wager(
                participant = participant
            )
            new_straightwager.set_fields_to_base()
            new_straightwager.save()
            straightwager = new_straightwager
        straightwager.win = each["win"]
        straightwager.place = each["place"]
        straightwager.show = each["show"]
        straightwager.save()


def process_race_data(race, race_data):
    print("process race data")
    for each in race_data:
        dog = get_dog(each["dogname"])
        participant = get_participant(race, dog)
        post_weight = get_post_weight(
            dog.name,
            race.chart.program.date)
        participant.post = each["post"]
        if post_weight:
            participant.post_weight = post_weight
        if each["off"]:
            participant.off = each["off"]
        if each["eighth"]:
            participant.eighth = each["eighth"]
        if each["straight"]:
            participant.straight = each["straight"]
        if each["final"]:
            participant.final = each["final"]
        if each["lengths_behind"]:
            participant.lengths_behind = each["lengths_behind"]
        if each["actual_running_time"]:
            try:
                participant.actual_running_time = each["actual_running_time"]
            except:
                pass
        participant.comment = each["comment"]
        participant.save()

def save_exotic_bets(race, exotic_bets):

    for bet in exotic_bets:
        if bet["name"] == "EXACTA":
            create_exacta(race, bet["posts"], cost, bet["payout"])
        elif bet["name"] == "QUINELLA":
            create_quiniela(race, bet["posts"], cost, bet["payout"])
        elif bet["name"] == "TRIFECTA":
            create_trifecta(race, bet["posts"], cost, bet["payout"])
        elif bet["name"] == "SUPERFECTA":
            create_superfecta(race, bet["posts"], cost, bet["payout"])

def handle_race(race, race_setting, race_data, single_bets, exotic_bets):
    build_weather_from_almanac(race.chart.program)
    if race_setting:
        save_race_info(race, race_setting)
    process_race_data(race, race_data)

    save_single_bets(race, single_bets)
    # save single bets

    save_exotic_bets(race, exotic_bets)
    if race.grade and race.grade.value:
        build_race_metrics(race)

def single_url_test(results_url, tds, chart):
    print("\n{}\n".format(results_url))
    if not "GWD$20180915S05" in results_url:
        raw_setting = get_raw_setting(tds)
        print("Raw Setting: {}\n".format(raw_setting))
        if raw_setting:
            race_setting = get_race_setting(raw_setting)
            race_number = results_url[-2:]
            if race_setting:
                page_rows = get_node_elements(results_url, '//tr')
                race_rows = get_rows_of_length(page_rows, 10)
                bet_rows = get_rows_of_length(page_rows, 5)
                print("Bet rows length: {}".format(len(bet_rows)))
                single_bets = None
                if len(bet_rows) > 1:
                    single_bets = get_single_bets(bet_rows)
                exotic_bets = get_exotic_bets(results_url)
                print("Exotic bets length: {}".format(len(exotic_bets)))
                print("Race rows:")
                race_data = get_race_data(race_rows)
                # print("Race data: {}".format(race_data))
                # print(race_data)
                # print("Chart: {}".format(chart))
                if chart:
                    print("has chart")
                    program = chart.program
                    print("Program: {}".format(program))
                    if race_number.isnumeric():
                        race = get_race(chart, race_number)
                        if len(race_data) > 0:
                            handle_race(race, race_setting, race_data, single_bets, exotic_bets)
                    else:
                        print("race number not numeric")
                    print("DONE")
                else:
                    print_race_setting(raw_setting, race_number, race_setting)
                    print_single_bets(single_bets)
                    print_exotic_bets(exotic_bets)
                    print(len(race_data))
                    if len(race_data) > 0:
                        print_race_data(race_data)
        else:
            print("No raw setting")



def save_race_info(race, race_setting):
    if race_setting:
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
            formatted_date = get_date_from_ymd(year, month, day)
            program = get_program(venue, formatted_date)
            tds = get_node_elements(results_url, '//td')
            if len(tds) > 85:
                single_url_test(results_url, tds, get_chart(program, time))
            else:
                failed_attempts += 1
            number += 1
