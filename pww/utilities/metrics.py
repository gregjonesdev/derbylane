from pww.models import Metric, Prediction

past_race_count = 7
minimum_participations = 2

def get_raw_fastest_time(participations):
      fastest_time = None
      for participation in participations:
          current_time = participation.actual_running_time
          if current_time:
              if not fastest_time or current_time < fastest_time:
                  fastest_time = current_time
      return fastest_time
      

def get_prior_participations(dog, target_date, distance, race_count):
    return dog.participant_set.filter(
        race__chart__program__date__lt=target_date,
        race__distance=distance,
        race__condition="F",
        final__isnull=False).order_by(
            '-race__chart__program__date')[:race_count]


def get_raw_participant_metrics(participant, distance):
    target_grade_value = participant.race.grade.value
    dog = participant.dog
    target_date = participant.race.chart.program.date
    participations = get_prior_participations(
        dog,
        target_date,
        distance,
        past_race_count)
    if len(participations) >= minimum_participations:
        raw_metrics = {
            "raw_fastest_time": get_raw_fastest_time(participations),
            "win_percent": None,
            "place_percent": None,
            "show_percent": None,
            "break_avg": None,
            "eighth_avg": None,
            "straight_avg": None,
            "finish_avg": None,
            "grade_avg": None,
            "time_seven": None,
            "time_three": None,
            "upgrade": None,
            "age": None,
            "sex": None,
            "set_weight": None,
            "post_factor": None,
            "temp_factor": None,
            "rh_factor": None,
        }
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
        if is_complete:
            raw_metrics.append(participant.final)
        else:
            raw_metrics.append(scheduled_final_value)
        return raw_metrics
    else:
        return None

def get_raw_race_metrics(race):
    raw_race_metrics = []
    for participant in race.participant_set.all():
        raw_metrics = get_raw_participant_metrics(participant, race.distance)
        if raw_metrics:
            raw_race_metrics.append(raw_metrics)
    return raw_race_metrics


# START HERE
def calculate_scaled_race_metrics(race):
    raw_race_metrics = get_raw_race_metrics(race)
