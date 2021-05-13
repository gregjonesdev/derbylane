import requests

from lxml import html


def get_node_elements(url, string):
    return get_node(url).xpath(string)

def get_node(url):
    r = requests.get(url)
    data = r.content.decode(r.encoding)
    return html.fromstring(data)


def get_attribute_node(url, element, attribute, value):
    query_string = "{}[@{}={}]".format(element, attribute, value)
    return get_node_elements(
        url,
        query_string)
