import requests
from lxml import html

from miner.utilities.urls import (
    results_url,
)

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
