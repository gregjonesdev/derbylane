from miner.utilities.common import (
    get_attribute_elements,
    get_node_elements,
    clean_race_setting,
    save_race_settings,
    get_dog,
)

from miner.utilities.models import save_participant

def get_parsed_race_setting(url):
    td = get_attribute_elements(
        url,
        "td",
        "valign",
        "middle")[0]
    return clean_race_setting(td)

def get_participant_entry_anchors(entries_url):
    return get_attribute_elements(
        entries_url,
        "a",
        "style",
        "padding:1px;12px;color:#f4780d;text-transform:uppercase;")

def populate_race(entries_url, race):
    post_count = 1
    for anchor in get_participant_entry_anchors(entries_url):
        dog_name = anchor.text
        save_participant(race, post_count, get_dog(dog_name))
        post_count += 1

def process_entries_url(entries_url, race):
    parsed_setting = get_parsed_race_setting(entries_url)
    print(parsed_setting)
    save_race_settings(race, parsed_setting)
    populate_race(entries_url, race)

def has_entries(url):
    trs = get_node_elements(url, "//tr")
    return len(trs) > 34
