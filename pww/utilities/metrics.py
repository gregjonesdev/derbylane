from pww.models import Metric, Prediction
import datetime

past_race_count = 7
minimum_participations = 2
x_values = [1, 2, 3, 4, 5, 6, 7, 8]


from scipy.optimize import curve_fit
from numpy import arange
#
def objective(x, a, b, c, d):
    return a*x + b*x**2 + c*x**3 + d

def objective3(x, a, b, c):
    return a*x + b*x**2 + c


def objective2(x, a, b):
    return a*x + b


def normalize(value, list):
    max_avg = max(list)
    min_avg = min(list)
    factor = (max_avg - value)/(max_avg - min_avg)
    if value >= max_avg:
        return 1
    elif value <= min_avg:
        return 0
    else:
        return factor


def build_avg_obj(posts_obj):
    avg_obj = {}
    for each in posts_obj.keys():
        avg_obj[each] = get_average(posts_obj[each])
    return avg_obj


def build_posts_obj(participations):
    posts_obj = {}
    for item in participations:
        post = item.post
        final = item.final
        if final and post:
            str_post = str(post)
            if not str_post in posts_obj.keys():
                posts_obj[str_post] = []
            posts_obj[str_post].append(final)
    return posts_obj


def build_temp_obj(participations):
    print('build temp obj')
    posts_obj = {}
    for item in participations:
        print(item.race.chart.get_rh())
        print(item.race.chart.get_racetemp())
        # post = item.post
        # final = item.final
        # if final and post:
        #     str_post = str(post)
        #     if not str_post in posts_obj.keys():
        #         posts_obj[str_post] = []
        #     posts_obj[str_post].append(final)
    return posts_obj


def curve_fitting(value, x_values, y_values):
    if len(x_values) < 2:
        return y_values[0]
    else:
        popt, _ = curve_fit(objective2, x_values, y_values)
        a, b = popt
        return objective2(value, float(a), float(b))



def get_factor(initial_x, x_values, y_values):



    if str(initial_x) in x_values:
        index = x_values.index(target_post)
        target_value = y_values[index]
    else:
        target_value = curve_fitting(initial_x, x_values, y_values)
    return normalize(target_value, y_values)



def calculate_factor(target_post, posts_obj):
    avg_obj = build_avg_obj(posts_obj)
    post_avg = get_factor(target_post, avg_obj)
    for each in sorted(avg_obj.keys()):
        print("{}: {}".format(each, avg_obj[each]))
    print("---- Calculated factor ----")
    print("{}: {}".format(target_post, post_avg))
    return post_avg





def get_postweight_average(participations):
    values = []
    for item in participations:
        post_weight = item.post_weight
        if post_weight:
            values.append(post_weight)
    return get_average(values)


def get_age(participant):
    target_date = participant.race.chart.program.date
    whelp_date = participant.dog.whelp_date
    age = target_date - target_date
    return age.days


def upgrade(participations, target_grade):
    upgrade = 3
    for each in participations:
        grade = each.race.grade
        if grade and isinstance(grade.value, int):
            if target_grade < grade.value:
                return upgrade
            upgrade -= 1
            if upgrade < 1:
                return 0
    return upgrade


def time_average(participations):
    values = []
    for item in participations:
        actual_running_time = item.actual_running_time
        if actual_running_time:
            values.append(actual_running_time)
    return get_average(values)


def grade_average(participations):
    # the average racing grade of the dog (A-D) of the last 7 races
    values = []
    for item in participations:
        if item.race.grade:
            values.append(item.race.grade.value)
    return get_average(values)


def get_break_average(participations):
    # the dog’s average position out of the starting box
    values = []
    for item in participations:
        off = item.off
        if off:
            values.append(off)
    return get_average(values)


def get_eighth_average(participations):
    # the dog’s average position out of the starting box
    values = []
    for item in participations:
        eighth = item.eighth
        if eighth:
            values.append(eighth)
    return get_average(values)


def get_straight_average(participations):
    # the dog’s average position out of the starting box
    values = []
    for item in participations:
        straight = item.straight
        if straight:
            values.append(straight)
    return get_average(values)


def get_finish_average(participations):
    # the dog’s average finishing position
    values = []
    for item in participations:
        final = item.final
        if final:
            values.append(final)
    return get_average(values)


def get_average(data_list):
    Not_none_values = filter(None.__ne__, data_list)
    list_of_values = list(Not_none_values)

    if len(list_of_values) > 0:
        return float(sum(list_of_values)/len(list_of_values))
    return None


def get_raw_fastest_time(participations):
      fastest_time = None
      for participation in participations:
          current_time = participation.actual_running_time
          if current_time:
              if not fastest_time or current_time < fastest_time:
                  fastest_time = current_time
      return fastest_time

def get_position_percent(participations, position):
    if len(participations) > 0:
        position_finishes = 0
        for each in participations:
            if each.final == position:
                position_finishes += 1
            return (position_finishes/len(participations))
    else:
        return None


def get_prior_participations(dog, target_date, distance, race_count):
    return dog.participant_set.filter(
        race__chart__program__date__lt=target_date,
        race__distance=distance,
        race__condition="F",
        final__isnull=False).order_by(
            '-race__chart__program__date')[:race_count]


def is_complete(participant_metrics):
    count = 0
    for each in participant_metrics.values():
        # print(each)
        if not each == None:
            count += 1
    # print(count)
    # print(len(participant_metrics.keys()))
    return count == len(participant_metrics.keys())


def get_raw_participant_metrics(participant, distance):
    target_grade_value = participant.race.grade.value
    dog = participant.dog
    target_date = participant.race.chart.program.date
    participations = get_prior_participations(
        dog,
        target_date,
        distance,
        past_race_count)
    build_temp_obj(participations)
    raise SystemExit(0)
    if len(participations) >= minimum_participations:
        raw_metrics = {
            "raw_fastest_time": get_raw_fastest_time(participations),
            "win_percent": get_position_percent(participations, 1),
            "place_percent": get_position_percent(participations, 2),
            "show_percent": get_position_percent(participations, 3),
            "break_avg": get_break_average(participations),
            "eighth_avg": get_eighth_average(participations),
            "straight_avg": get_straight_average(participations),
            "finish_avg": get_finish_average(participations),
            "grade_avg": grade_average(participations),
            "time_seven": time_average(participations[:7]),
            "time_three": time_average(participations[:3]),
            "upgrade": upgrade(participations[:3], target_grade_value),
            "age": get_age(participant),
            "sex": participant.dog.sex,
            "post_weight_avg": get_postweight_average(participations),
            "post_factor": calculate_factor(
                participant.post,
                build_posts_obj(participations)),
            # "temp_factor": None,
            # "rh_factor": None,
            "final": participant.final,
        }
        # print(is_complete(raw_metrics))
        # raw_metrics = []
        # raw_metrics.append(str(participant.uuid))
        # raw_metrics.append(
        #     get_raw_fastest_time(participations))
        # raw_metrics.append(
        #     get_position_percent(participations, 1)
        # )
        # raw_metrics.append(
        #     get_position_percent(participations, 2)
        # )
        # raw_metrics.append(
        #     get_position_percent(participations, 3)
        # )
        # raw_metrics.append(
        #     get_break_average(participations)
        # )
        # raw_metrics.append(
        #     get_finish_average(participations)
        # )
        # raw_metrics.append(
        #     grade_average(participations)
        # )
        # raw_metrics.append(
        #     time_average(participations[:7])
        # )
        # raw_metrics.append(
        #     time_average(participations[:3])
        # )
        # raw_metrics.append(
        #     upgrade(
        #         participations[:3],
        #         target_grade_value)
        # )

        # if is_complete:
        #     raw_metrics.append(participant.final)
        # else:
        #     raw_metrics.append(scheduled_final_value)
        # return raw_metrics
    else:
        return None

def get_raw_race_metrics(race):
    raw_race_metrics = []
    for participant in race.participant_set.all():
        raw_metrics = get_raw_participant_metrics(participant, race.distance)
        # if raw_metrics:
        #     raw_race_metrics.append(raw_metrics)
    return raw_race_metrics


# START HERE
def calculate_scaled_race_metrics(race):
    raw_race_metrics = get_raw_race_metrics(race)
