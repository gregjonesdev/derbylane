import requests

from lxml import html

from miner.utilities.urls import (
    results_url,
)

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

def check_for_results(race, page_data):
    td_count = len(page_data)
    print(td_count)
    if td_count > 50:
        print('process results')
        if td_count > 110:
            print('process bets')


def build_race(venue, year, month, day, time, number):
    program = get_program(
        venue,
        year,
        month,
        day)
    chart = get_chart(program, time)
    return get_race(chart, number)

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


def get_node_elements(url, string):
    return get_node(url).xpath(string)

def get_node(url):
    r = requests.get(url)
    data = r.content.decode(r.encoding)
    return html.fromstring(data)

def has_race(page_data):
    td_count = len(page_data)
    if td_count > 20:
        return True

def save_race_data(url):
    print("save_race_data")
    print(url)
