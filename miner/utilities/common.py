import requests
from datetime import datetime, date
from miner.utilities.urls import arff_directory
from lxml import html
from miner.utilities.constants import bcolors

def get_node_elements(url, string):
    return get_node(url).xpath(string)

def get_node(url):
    r = requests.get(url)
    data = r.content.decode(r.encoding)
    return html.fromstring(data)


def get_attribute_elements(url, element, attribute, value):
    query_string = '//{}[@{}="{}"]'.format(
        element,
        attribute,
        value)
    return get_node_elements(
        url,
        query_string)

def force_date(input):
    if isinstance(input, str):
        return datetime.strptime(input, "%Y-%m-%d").date()
    else:
        return input

def get_race_key(venue_code, distance, grade_name):
    return "{}_{}_{}".format(venue_code, distance, grade_name)


def two_digitizer(integer):
    if integer < 10:
        return "0{}".format(integer)
    else:
        return integer


def get_formatting(max, value):
    formatting = ""
    if value > 2.00:
        formatting += bcolors.OKGREEN
        formatting += bcolors.BOLD
    return formatting + "${:.2f}".format(value) + bcolors.ENDC
