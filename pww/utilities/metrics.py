from pww.models import Metric, Prediction

def get_prior_participations(dog, target_date, distance, number):
    raw_priors = dog.participant_set.filter(
        race__chart__program__date__lt=target_date,
        race__distance=distance,
        race__condition="F",
        final__isnull=False).order_by(
            '-race__chart__program__date')[:number]
    filtered_priors = []
    for part in raw_priors:
        print(part.finish)
        # if part.final and part.race.distance:
        #     if min_distance <= part.race.distance <= max_distance:
        #         filtered_priors.append(part)
    return filtered_priors

def get_raw_participant_metrics(participant, distance):
    target_grade_value = participant.race.grade.value
    dog = participant.dog
    target_date = participant.race.chart.program.date
    participations = get_prior_participations(
        dog,
        target_date,
        distance,
        7)
    if len(participations)>1:
        raw_metrics = {
            "raw_fastest_time": None

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
