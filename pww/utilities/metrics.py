from pww.models import Metric, Prediction
import datetime
from rawdat.models import Participant
from django.core.exceptions import ObjectDoesNotExist

past_race_count = 7
minimum_participations = 2
x_values = [1, 2, 3, 4, 5, 6, 7, 8]

from miner.utilities.models import save_dog_info
from miner.utilities.common import force_date

from scipy.optimize import curve_fit
from numpy import arange

def objective(x, a, b, c, d):
    return a*x + b*x**2 + c*x**3 + d

def objective3(x, a, b, c):
    return a*x + b*x**2 + c


def objective2(x, a, b):
    return a*x + b


def normalize(value, list):
    max_avg = max(list)
    min_avg = min(list)
    if max_avg > min_avg:
        factor = (max_avg - value)/(max_avg - min_avg)
    if value >= max_avg:
        return 1
    elif value <= min_avg:
        return 0
    else:
        return factor


def build_avg_obj(orig_object):
    avg_obj = {}
    for each in orig_object.keys():
        print(get_average(orig_object[each]))
        avg_obj[each] = get_average(orig_object[each])
    return avg_obj

def add_to_obj(value, key, target_obj):
    str_key = str(key)
    if not str_key in target_obj.keys():
        target_obj[str_key] = []
    target_obj[str_key].append(value)
    return target_obj


def build_posts_object(participations):
    posts_object = {}
    for item in participations:
        post = item.post
        final = item.final
        if final and post:
            posts_object = add_to_obj(final, post, posts_object)
    return posts_object


def build_temp_object(participations):
    temp_object = {}
    for item in participations:
        post = item.post
        temp = item.race.chart.get_racetemp()
        final = item.final
        if final and temp:
            temp_object = add_to_obj(final, temp, temp_object)
    return temp_object


def build_rh_object(participations):
    rh_object = {}
    for item in participations:
        post = item.post
        rh = item.race.chart.get_rh()
        final = item.final
        if final and rh:
            rh_object = add_to_obj(final, rh, rh_object)
    return rh_object


def curve_fitting(value, x_values, y_values):
    if len(x_values) < 2:
        return y_values[0]
    else:
        popt, _ = curve_fit(objective2, x_values, y_values)
        a, b = popt
        return objective2(value, float(a), float(b))


def convert_dictlist_to_list(dict_list):

    list = []
    for each in dict_list:
        list.append(float(each))
    # print(list)
    return list

def get_factor(initial_x, x_values, y_values):
    if initial_x:
        if float(initial_x) in x_values:
            index = x_values.index(initial_x)
            target_value = y_values[index]
        else:
            target_value = curve_fitting(initial_x, x_values, y_values)
        return normalize(target_value, y_values)



def calculate_factor(target_y, raw_object):
    print("raw obj:")
    print(raw_object)
    avg_obj = build_avg_obj(raw_object)
    print("average obj:")
    print(avg_obj)
    factored_avg = get_factor(
        target_y,
        convert_dictlist_to_list(avg_obj.keys()),
        convert_dictlist_to_list(avg_obj.values()))

    # for each in sorted(avg_obj.keys()):
    #     print("{}: {}".format(each, avg_obj[each]))
    # print("---- Calculated factor ----")
    # print("{}: {}".format(target_y, factored_avg))
    return factored_avg


def get_postweight_average(participations):
    values = []
    for item in participations:
        post_weight = item.post_weight
        if post_weight:
            values.append(post_weight)
    return get_average(values)


def get_age(participant):
    # print('get_age')
    save_dog_info(participant.dog)
    target_date = force_date(participant.race.chart.program.date)
    dog = participant.dog
    if dog.litter:
        whelp_date = force_date(dog.litter.whelp_date)
        # print(target_date)
        # print(whelp_date)

        age = target_date - whelp_date
        # print(age)
        # print(age.days)
        return age.days


def get_sex(participant):
    if not participant.dog.sex:
        save_dog_info(participant.dog)
    return participant.dog.sex


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
    print("priors")
    print("any parts?")
    print(len(dog.participant_set.all()))
    return dog.participant_set.filter(
        race__chart__program__date__lt=target_date,
        race__distance=distance,
        race__condition="F",
        final__isnull=False).order_by(
            '-race__chart__program__date')[:race_count]


def is_complete(participant_metrics):
    count = 0
    for each in participant_metrics.values():
        if not each == None:
            count += 1
    return count == len(participant_metrics.keys())


def get_raw_participant_metrics(participant, distance):
    if participant.race.grade:
        target_grade_value = participant.race.grade.value
        dog = participant.dog
        target_date = participant.race.chart.program.date
        participations = get_prior_participations(
            dog,
            target_date,
            distance,
            past_race_count)

        chart = participant.race.chart
        print("participations: {}".format(len(participations)))
        if len(participations) >= minimum_participations:
            raw_metrics = {
                "participant": participant,
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
                    build_posts_object(participations)),
                "temp_factor": calculate_factor(
                    chart.get_racetemp(),
                    build_temp_object(participations)),
                "rh_factor": calculate_factor(
                    chart.get_rh(),
                    build_rh_object(participations)),
                # "final": participant.final,
            }
            # if is_complete(raw_metrics):
            return raw_metrics

def scale_metrics(raw_metrics):
    slowest_time = get_slowest_raw_time(raw_metrics)
    scaled_metrics = raw_metrics
    for metric in scaled_metrics:
        if metric["raw_fastest_time"]:
            metric["scaled_fastest_time"] = slowest_time - metric["raw_fastest_time"]
        else:
            metric["scaled_fastest_time"] = slowest_time
    return scaled_metrics

def get_slowest_raw_time(raw_race_metrics):
    raw_times = []
    for metric in raw_race_metrics:
        current_raw_time = metric["raw_fastest_time"]
        if current_raw_time:
            raw_times.append(current_raw_time)
    if len(raw_times) > 0:
        return max(raw_times)
    else:
        return None


def get_raw_race_metrics(race):
    raw_race_metrics = []
    for participant in race.participant_set.all():
        raw_metrics = get_raw_participant_metrics(participant, race.distance)
        # print("RAW PART METRICS: {}".format(len(raw_metrics)))
        if raw_metrics:
            raw_race_metrics.append(raw_metrics)
    return raw_race_metrics


def calculate_scaled_race_metrics(race):
    raw_race_metrics = get_raw_race_metrics(race)
    print("RAW RACE METRICS: {}".format(len(raw_race_metrics)))
    return scale_metrics(raw_race_metrics)

def save_metrics(metrics):
    participant = metrics["participant"]
    try:
        existing_metric = Metric.objects.get(participant=participant)
        print("metric already exists. updating {}".format(participant.uuid))
    except ObjectDoesNotExist:
        new_metric = Metric(
            participant=metrics["participant"]
        )
        print("new")
        new_metric.set_fields_to_base()
        existing_metric = new_metric
        # print("CREATED NEW METRIC FOR: {}".format(participant.uuid))
    # print(participant.final)
    # print("{} {} {} {}".format(participant.race.chart.program.date, participant.race.chart.program.venue.code, participant.race.grade.name, participant.race.distance ))
    existing_metric.scaled_fastest_time = metrics["scaled_fastest_time"]
    existing_metric.win = metrics["win_percent"]
    existing_metric.place = metrics["place_percent"]
    existing_metric.show = metrics["show_percent"]
    existing_metric.break_avg = metrics["break_avg"]
    existing_metric.eighth_avg = metrics["eighth_avg"]
    existing_metric.straight_avg = metrics["straight_avg"]
    existing_metric.finish_avg = metrics["finish_avg"]
    existing_metric.grade_avg = metrics["grade_avg"]
    existing_metric.time_seven = metrics["time_seven"]
    existing_metric.time_three = metrics["time_three"]
    existing_metric.upgrade = metrics["upgrade"]
    existing_metric.age = metrics["age"]
    existing_metric.sex = metrics["sex"]
    existing_metric.post_weight_avg = metrics["post_weight_avg"]
    existing_metric.post_factor = metrics["post_factor"]
    existing_metric.temp_factor = metrics["temp_factor"]
    existing_metric.rh_factor =  metrics["rh_factor"]
    if participant.final:
        existing_metric.final = participant.final
    existing_metric.save()



# START HERE
def build_race_metrics(race):
    print("BUILD RACE METRICS ")
    scaled_race_metrics = calculate_scaled_race_metrics(race)
    print(len(scaled_race_metrics))
    for metrics in scaled_race_metrics:
        save_metrics(metrics)
