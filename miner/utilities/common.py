import requests
from datetime import datetime, date
from miner.utilities.urls import arff_directory, build_dog_profile_url
from django.core.exceptions import ObjectDoesNotExist
from rawdat.models import Grade
from lxml import html
from miner.utilities.constants import (
    bcolors,
    bad_characters,
    art_skips,
    grade_skips,
    post_weight,
    zero_lengths,
    position_skips,
    length_converter,
    max_lengths)

from rawdat.models import Dog, Litter


def save_sex_and_color(dog, elements):
    try:
        text = elements[0].text
        sex_and_color = text.split("/")
        save_sex(dog, sex_and_color[0])
        save_color(dog, sex_and_color[1])
    except:
        pass

def get_litter(sire, dam, whelp_date):
    try:
        litter = Litter.objects.get(
            sire=sire,
            dam=dam,
            whelp_date=whelp_date
        )
    except ObjectDoesNotExist:
        new_litter = Litter(
            sire=sire,
            dam=dam,
            whelp_date=whelp_date
        )
        new_litter.set_fields_to_base()
        new_litter.save()
        litter = new_litter
    return litter


def get_parent_name(url, class_attr):
    # print(url)
    return get_node_elements(
        url,'//td[@class="{}"]//a'.format(class_attr))[0].text

def save_dog_info(dog):
    url = build_dog_profile_url(dog.name)
    # print(url)
    whelp_date = None
    if not dog.litter:
        try:
            whelp_date = get_node_elements(url, '//td[@class="it4"]//em')[0].text
        except IndexError:
            pass
        sire_name = get_parent_name(url, "it2")
        sire, dam = None, None
        if sire_name:
            sire = get_dog(sire_name)
        dam_name = get_parent_name(url, "it4")
        if dam_name:
            dam = get_dog(dam_name)
        if sire and dam and whelp_date:
            litter = get_litter(sire, dam, whelp_date)
            dog.litter = litter
    dog.save()
    save_sex_and_color(
        dog,
        get_node_elements(url, '//td[@class="it2"]//em'))

def get_dog(name):
    print(name)
    try:
        dog = Dog.objects.get(name=name.upper())
    except ObjectDoesNotExist:
        new_dog = Dog(
            name=name.upper()
        )
        new_dog.set_fields_to_base()
        new_dog.save()
        dog = new_dog
        save_dog_info(dog)
    return dog

def get_grade(raw_grade):
    print("get_grade")

    print(raw_grade)
    stripped_grade = raw_grade.strip().upper()
    if stripped_grade:
        if stripped_grade in grade_skips:
            print("Skiiped")
            print(grade_skips)
            return None
        try:
            grade = Grade.objects.get(name=stripped_grade)
        except ObjectDoesNotExist:
            new_grade = Grade(
                name=stripped_grade
            )
            new_grade.set_fields_to_base()
            new_grade.save()
            grade = new_grade
        return grade
    else:
        print("nothing")
        return None

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

def remove_line_breaks(text):
    return text.replace("\n", "")

def remove_tabs(text):
    return text.replace("\t", "")

def remove_extra_spaces(text):
    return text.replace("  ", " ")

def get_race_distance(race_distance):
    return(int(race_distance))

def clean_race_setting(td):
    single_line_text = remove_line_breaks(td.text)
    untabbed_text = remove_tabs(single_line_text)
    unspaced_text = remove_extra_spaces(untabbed_text)
    return unspaced_text.split()

def save_race_settings(race, parsed_setting):
    try:
        race.grade = get_grade(parsed_setting[2])
        race.distance = get_race_distance(parsed_setting[3])
    except IndexError:
        print("Index Error:")
        print(parsed_setting)
    race.save()
