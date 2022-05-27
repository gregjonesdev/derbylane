from miner.utilities.common import get_attribute_elements

def remove_line_breaks(text):
    return text.replace("\n", "")

def remove_tabs(text):
    return text.replace("\t", "")

def remove_extra_spaces(text):
    return text.replace("  ", " ")

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
