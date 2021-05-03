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




def build_daily_charts(venue, year, month, day):
    for time in chart_times:
        scan_chart(venue, year, month, day, time)

def scan_chart(venue, year, month, day, time):
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
        if has_race_data(target_url):
            program = get_program(
                venue,
                year,
                month,
                day)
            chart = get_chart(program, time)
            race = get_race(
                chart,
                number)
            save_race_data(target_url)
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

def has_race_data(url):
    td_count = len(get_node_elements(url, '//td'))
    if td_count > 20:
        return True

def save_race_data(url):
    print("save_race_data")
    print(url)
