from miner.utilities.common import get_attribute_elements
from rawdat.models import Grade, Condition

def remove_line_breaks(text):
    return text.replace("\n", "")

def remove_tabs(text):
    return text.replace("\t", "")

def remove_extra_spaces(text):
    return text.replace("  ", " ")

def get_race_number(race_number):
    return(int(race_number))

def get_race_distance(race_distance):
    return(int(race_distance))

def get_race_grade(race_grade):
    try:
        grade = Grade.objects.get(name=race_grade)
    except ObjectDoesNotExist:
        grade = Grade(
            name=race_grade
        )
        grade.set_fields_to_base()
        grade.save()
    return grade

def get_race_condition(race_condition):
    try:
        condition = Condition.objects.get(name=race_condition)
    except ObjectDoesNotExist:
        condition = Condition(
            name=race_condition
        )
        condition.set_fields_to_base()
        condition.save()
    return condition

def parse_race_setting(td):
    single_line_text = remove_line_breaks(td.text)
    untabbed_text = remove_tabs(single_line_text)
    unspaced_text = remove_extra_spaces(untabbed_text)
    race_setting_list = unspaced_text.split()
    print(race_setting_list)

def process_url(url):
    print("process_race")
    # print(len(tds))
    # for td in tds:
    #     print(td)

    middle_aligned_tds = get_attribute_elements(
        url,
        "td",
        "style",
        "vertical-align: middle;")
    race_setting = parse_race_setting(middle_aligned_tds[1])
    race_number = get_race_number(race_setting[1])
    race_grade = get_race_grade(race_setting[1])
    race_distance = get_race_distance(race_setting[1])
    race_condition = get_race_condition(race_setting[1])
