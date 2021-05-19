import requests
from datetime import datetime, date
from lxml import html


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
        return date.strptime(input, "%Y-%m-%d")
    else:
        return input
