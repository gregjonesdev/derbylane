import re
from django.core.exceptions import ObjectDoesNotExist
from miner.utilities.urls import (
    results_url,
    all_race_results,
    all_race_suffix,
    entries_url,
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
    )

from rawdat.utilities.methods import (
    get_date_from_ymd,
    get_race
)

from miner.utilities.models import (
    update_participant,
    save_sex,
    save_post_weight,
    save_race_info,
    get_participant,
    create_single,
    get_dog,
    get_bettype,
    get_grade,
    get_chart,
    get_program,
    create_exacta,
    create_quiniela,
    create_trifecta,
    create_superfecta,
)

from miner.utilities.weather import get_forecast_url

from miner.utilities.common import get_node_elements

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
    i = 2
    while i < 5:
        split_position = split_position_lengths(row[i].text)
        if len(split_position) > 0:
            positions.append(split_position[0])
        else:
            positions.append(None)
        i += 1
    return positions


def get_race_rows(div_tds):
    race_rows = []
    for div_td in div_tds:
        race_rows.append(div_td.getparent().getparent())
    return race_rows

def get_post_weight(dog_name, date):
    target_url = "{}{}{}".format(all_race_results, dog_name, all_race_suffix)
    string_date = "{}".format(date)
    entries = get_node_elements(target_url, '//td[@class="raceline"]')
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
    positions = get_positions(row)
    final_lengths = get_final_and_lengths_behind(
        split_position_lengths(row[5].text))
    final = final_lengths[0]
    lengths_behind = final_lengths[1]
    dog = get_dog(row[0][0].text)
    participant = get_participant(race, dog)
    post_weight = get_post_weight(
        participant.dog.name,
        race.chart.program.date)
    update_participant(
        participant,
        post_weight,
        get_position(positions[0]),
        get_position(row[1].text),
        get_position(positions[1]),
        get_position(positions[2]),
        get_position(final),
        get_time(row[6].text),
        lengths_behind,
        row[9].text.strip())


def get_results(div_tds, race):
    race_rows = get_race_rows(div_tds)
    for row in race_rows:
        if len(row) is 10:
            parse_row(row, race)

def check_for_results(results_url, race):
    print("check for results")
    # div_tds = get_node_elements(results_url, '//td//div')
    # td_count = len(div_tds)
    # print(td_count)
    # if td_count > 50:
    #     get_results(div_tds, race)
    #     for each in page_data:
    #         print("{}: {}".format(page_data.index(each), each.text))
    #     print(results_url)
    #     if td_count > 110:
    #         process_combo_bets(race, results_url)
    #         process_dog_bets(race, page_data)


def process_combo_bets(race, target_url):
    print("process combo bets")
    for each in get_node_elements(target_url, '//p'):
        split_text = each.text.split()
        bet_prices = []
        if len(split_text) > 0:
            print(split_text)
            for string in split_text:
                if "$" in string or "." in string:
                    bet_prices.append(string)
                elif string.isalpha() and not 'paid' in string.lower():
                    combo_name = get_combo_name(string.upper())
                elif "/" in string:
                    posts = string.split("/")

            cost = get_dollar_amount(bet_prices[0])
            payout = get_dollar_amount(bet_prices[1])

            if cost and payout and bet_prices and posts:
                print("cost: {}".format(cost))
                print("payout: {}".format(payout))
                print("name: {}".format(combo_name))
                print("posts: {}".format(posts))
            else:
                print("uh oh @ 203: {}".format(split_text))
                raise SystemExit(0)

            if combo_name == "Exacta":
                create_exacta(race, posts, cost, payout)
            elif combo_name == "Quiniela":
                create_quiniela(race, posts, cost, payout)
            elif combo_name == "Trifecta":
                create_trifecta(race, posts, cost, payout)
            elif combo_name == "Superfecta":
                create_superfecta(race, posts, cost, payout)


    # raise SystemExit(0)

def get_dollar_amount(string):
    try:
        return float(string.replace("$", "").replace(",", ""))
    except:
        print("get_dollar_amt: couldnt float {}".format(string))
        raise SystemExit(0)

def get_combo_name(text):

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
        # print("Check on exotic: {}".format(text))
        # raise SystemExit(0)

def process_dog_bets(race, page_data):
    print("process dog betz ************")
    finisher_indices = [16, 22, 28]
    for index in finisher_indices:
        if isinstance(page_data[index].text, str):
            dog = get_dog(page_data[index].text.strip())
            participant = get_participant(race, dog)
            if participant:
                chart = race.chart
                program = chart.program
                print("{} / {} / {} / {}".format(
                    participant.dog.name,
                    page_data[index+1].text,
                    page_data[index+2].text,
                    page_data[index+3].text))

                process_singlepayouts(
                    participant,
                    [page_data[index+1].text,
                    page_data[index+2].text,
                    page_data[index+3].text])

def process_singlepayouts(participant, amounts):
    i = 0
    while i < 3:
        if isinstance(amounts[i], str):
            if amounts[i].strip():
                type = get_bettype(raw_types[i])
                amount = amounts[i]
                create_single(participant, type, amount)
        i += 1


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
    formatted_date = get_date_from_ymd(year, month, day)
    program = get_program(
        venue,
        formatted_date)
    try:
        weather_instance = Weather.objects.get(program=program)
    except ObjectDoesNotExist:
        get_forecast_url(program)
    chart = get_chart(program, time)
    return get_race(chart, number)

def is_race_heading_cell(text):
        if len(text) > 0:
            first_lower = text[0].lower()
            if first_lower.find('race') is 0:
                if first_lower.find('raced') < 0:
                    if not re.search('[a-zA-Z]', text[1]):
                        return True

def process_race(race, page_data, anchor_elements, div_elements):
    save_race_info(
        race,
        get_raw_setting(page_data))
    for each in div_elements:
        print(each)
    dognames = get_dognames(div_elements)
    print("len dognames: {}".format(len(dognames)))
    # populate_race(
    #     get_dognames(div_elements),
    #     race)

def get_dognames(div_elements):
    dognames = []
    for each in div_elements:
        print(each.text)
        # name = each.text
        # if not name in dognames:
        #     dognames.append(name)
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
    print("populate race")
    print(dognames)
    i = 0
    for name in dognames:
        if name and not name in no_greyhound_names:
            dog = get_dog(dognames[i])
            print(dog)
            post_position = i + 1
            print(post_position)
            participant = get_participant(race, dog)
            set_post(
                participant,
                post_position)
        i += 1

def scan_scheduled_charts(venue, year, month, day):
    for time in chart_times:
        number = 1
        failed_attempts = 0
        while failed_attempts <= allowed_attempts and number <= max_races_per_chart:
            entries_url = build_entries_url(
                venue.code,
                year,
                month,
                day,
                time,
                number)
            page_data = get_node_elements(entries_url, '//td')
            if len(page_data) > 20:
                pass
                # build race: create race object, save setting, populate
                formatted_date = get_date_from_ymd(year, month, day)
                program = get_program(
                    venue,
                    formatted_date)
                print("A+")
                print(program)
                # build_entries_race(venue, year, month, day, time, number)

                # race = build_race(venue, year, month, day, time, number)
                # anchor_elements = get_node_elements(entries_url, '//a')
                # save_race_info(
                #     race,
                #     get_raw_setting(page_data))
                # dognames = get_dognames(div_elements)
                # print("len dognames: {}".format(len(dognames)))
                # populate_race(
                #     get_dognames(div_elements),
                #     race)
            else:
                failed_attempts += 1
            number += 1    

def build_entries_race():
    # create race
    # populate
    pass

# def build_common_race(venue, date, time, number)



def build_results_race():
    # create race
    # populate
    pass

def scan_history_charts(venue, year, month, day):
    # load up results url
    # if has race
    # build race: create, save, populate
    # get results
    pass


def scan_chart_times(venue, year, month, day):
    for time in chart_times:
        number = 1
        failed_attempts = 0
        while failed_attempts <= allowed_attempts and number <= max_races_per_chart:
            entries_url = build_entries_url(
                venue.code,
                year,
                month,
                day,
                time,
                number)
            results_url = build_results_url(
                venue.code,
                year,
                month,
                day,
                time,
                number)
            page_data = get_node_elements(entries_url, '//td')
            print("-------------------------------------------------")
            print(entries_url)
            print(results_url)
            print("-------------------------------------------------")
            if has_race(page_data):
                print("has race data")
                race = build_race(venue, year, month, day, time, number)
                anchor_elements = get_node_elements(entries_url, '//a')
                process_race(race, page_data, anchor_elements)
                check_for_results(results_url, race)
                # div_elements = get_node_elements(results_url, '//div[@style="text-overflow:ellipsis;white-space:nowrap;width:5em;overflow:hidden;"]')

                # for each in div_elements:
                #     print(each)


                raise SystemExit(0)
                print(entries_url)
            else:
                failed_attempts += 1
            number += 1

def build_entries_url(venue_code, year, month, day, time, race_number):
    return "{}G{}${}{}{}{}{}".format(
        entries_url,
        venue_code,
        year,
        str(month).zfill(2),
        str(day).zfill(2),
        time,
        str(race_number).zfill(2))

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
    return len(page_data) > 20

def save_race_data(url):
    print("save_race_data")
    print(url)
