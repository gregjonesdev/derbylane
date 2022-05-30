from django.core.exceptions import ObjectDoesNotExist
from rawdat.models import (
    Color,
    Chart,
    Program,
    Race,
    Participant,
    Sizzle_Quinella,
    Sizzle_Exacta,
    Sizzle_Trifecta,
    Sizzle_Superfecta,
    StraightBetType,
    Straight_Bet,
    Grade,
    Straight_Wager,
    Dog,
    Condition
)

from miner.utilities.constants import (
    race_conditions,
    cost,
    grade_skips,
    distance_converter
)

from miner.utilities.common import get_node_elements

from miner.utilities.urls import (
    build_dog_profile_url,
)

def create_straight_bet(participant, type_name, payout):
    type = StraightBetType.objects.get(name=type_name)
    try:
        bet = Straight_Bet.objects.get(
            type=type,
            participant=participant,
            payout=payout
        )
    except ObjectDoesNotExist:
        bet = Straight_Bet(
            type=type,
            participant=participant,
            payout=payout
        )
        bet.set_fields_to_base()
        bet.save()



def create_quinella(race, posts, payout):
    try:
        bet = Sizzle_Quinella.objects.get(
            race=race,
            left_post__in=posts,
            right_post__in=posts
        )
    except ObjectDoesNotExist:
        new_bet = Sizzle_Quinella(
            race=race,
            left_post=posts[0],
            right_post=posts[1]
        )
        new_bet.set_fields_to_base()
        bet = new_bet
    bet.payout = payout
    bet.save()

def save_participant(race, post, dog):
    try:
        participant = Participant.objects.get(
            race=race,
            post=int(post)
        )
    except ObjectDoesNotExist:
        new_participant = Participant(
            race=race,
            post=int(post)
        )
        new_participant.set_fields_to_base()
        participant = new_participant
    participant.dog = dog
    participant.save()


def get_participant_from_post(race, post):
    try:
        return Participant.objects.get(
            race=race,
            post=int(post)
        )
    except:
        print("Error get part from post")
        for part in Participant.objects.filter(race=race):
            print(part.dog.name)
        raise SystemExit(0)


def create_exacta(race, posts, payout):
    try:
        bet = Sizzle_Exacta.objects.get(
            race=race,
            win_post=posts[0],
            place_post=posts[1],
        )
    except ObjectDoesNotExist:
        new_bet = Sizzle_Exacta(
            race=race,
            win_post=posts[0],
            place_post=posts[1],
        )
        new_bet.set_fields_to_base()
        bet = new_bet
    bet.payout = payout
    bet.save()




def create_trifecta(race, posts, payout):
    try:
        bet = Sizzle_Trifecta.objects.get(
            race=race,
            win_post=posts[0],
            place_post=posts[1],
            show_post=posts[2],
        )
    except ObjectDoesNotExist:
        new_bet = Sizzle_Trifecta(
            race=race,
            win_post=posts[0],
            place_post=posts[1],
            show_post=posts[2],
        )
        new_bet.set_fields_to_base()
        bet = new_bet
    bet.payout = payout
    bet.save()

def create_superfecta(race, posts, payout):
    try:
        bet = Sizzle_Superfecta.objects.get(
            race=race,
            win_post=posts[0],
            place_post=posts[1],
            show_post=posts[2],
            fourth_post=posts[3],
        )
    except ObjectDoesNotExist:
        new_bet = Sizzle_Superfecta(
            race=race,
            win_post=posts[0],
            place_post=posts[1],
            show_post=posts[2],
            fourth_post=posts[3],
        )
        new_bet.set_fields_to_base()
        bet = new_bet
    bet.payout = payout
    bet.save()





def get_straightwager(participant):
    try:
        straight_wager = Straight_Wager.objects.get(
            participant=participant
        )
    except ObjectDoesNotExist:
        new_straight = Straight_Wager(
            participant = participant
        )
        new_straight.set_fields_to_base()
        new_straight.save()
        straight_wager = new_straight
    return straight_wager









# def create_single(participant, type, payout):
#     try:
#         single = Single.objects.get(
#             participant=participant,
#             type=type
#         )
#     except ObjectDoesNotExist:
#         new_single = Single(
#             participant=participant,
#             type=type,
#             cost=cost,
#             payout=payout
#         )
#         new_single.set_fields_to_base()
#         new_single.save()

def update_participant(
    participant,
    post_weight,
    post,
    off,
    eighth,
    straight,
    final,
    actual_running_time,
    lengths_behind,
    comment):

    if post_weight:
        participant.post_weight = post_weight
    if post:
        participant.post = post
    if off:
        participant.off = off
    if eighth:
        participant.eighth = eighth
    if straight:
        participant.straight = straight
    if final:
        participant.final = final
    if lengths_behind:
        participant.lengths_behind = float(lengths_behind)
    if actual_running_time:
        participant.actual_running_time = actual_running_time
    if comment:
        participant.comment = comment
    participant.save()

def ask_user(attribute, value, check_url):
    print("Attention: {} is not a valid {}".format(value, attribute))
    print(check_url)
    while True:
        var = input("Please enter correct value: ")
        confirm = input("Press 'y' to confirm: ")
        if confirm in ["y", "Y"]:
            break
    return var

def update_race(race, grade, distance, condition):
    if grade:
        race.grade = grade
    if distance:
        race.distance = distance
    if condition:
        race.condition = condition
    race.save()

def save_post_weight(participant, post_weight):
    participant.post_weight = post_weight
    participant.save()

def is_grade(grade):
    return Grade.objects.filter(name=grade.upper()).exists()

# def save_race_info(race, raw_setting):
#     if raw_setting:
#         for item in raw_setting[:3]:
#             if is_grade(item):
#                 race.grade = get_grade(item)
#         for item in raw_setting:
#             if item in distance_converter:
#                 item = distance_converter[item]
#             try:
#                 item = int(item)
#                 if 100 < item < 900:
#                     distance = int(item)
#                     race.distance = distance
#             except:
#                 pass
#         for item in raw_setting[3:]:
#             if item.upper() in race_conditions:
#                 race.condition = item.upper()
#         race.save()


def get_chart(program, time):
    try:
        chart = Chart.objects.get(
            time=time,
            program=program
        )
    except ObjectDoesNotExist:
        new_chart = Chart(
            time=time,
            program=program
        )
        new_chart.set_fields_to_base()
        new_chart.save()
        chart = new_chart
    return chart

def get_program(venue, date):
    try:
        program = Program.objects.get(
            venue=venue,
            date=date
        )
    except ObjectDoesNotExist:
        new_program = Program(
            venue=venue,
            date=date
        )
        new_program.set_fields_to_base()
        new_program.save()
        program = new_program
    return program

def get_race(chart, number):
    try:
        race = Race.objects.get(
            chart=chart,
            number=number
        )
    except ObjectDoesNotExist:
        new_race = Race(
            chart=chart,
            number=number,
        )
        new_race.set_fields_to_base()
        new_race.save()
        race = new_race
    return race

def get_participant(race, dog):
    try:
        participant = Participant.objects.get(
            race=race,
            dog=dog
        )
    except ObjectDoesNotExist:
        new_participant = Participant(
            race=race,
            dog=dog,
        )
        new_participant.set_fields_to_base()
        new_participant.save()
        participant = new_participant

    return participant

# def create_combination(race, cost, type, payout):
#     try:
#         combination = Combination.objects.get(
#             race=race,
#             type=type
#         )
#     except ObjectDoesNotExist:
#         new_combination = Combination(
#             race=race,
#             type=type,
#             cost=cost,
#             payout=payout
#         )
#         new_combination.set_fields_to_base()
#         new_combination.save()



def get_condition(race_condition):
    try:
        condition = Condition.objects.get(name=race_condition)
    except ObjectDoesNotExist:
        condition = Condition(
            name=race_condition
        )
        condition.set_fields_to_base()
        condition.save()
    return condition


def get_color(name):
    try:
        color = Color.objects.get(name=name.upper())
    except ObjectDoesNotExist:
        new_color = Color(
            name=name.upper()
        )
        new_color.set_fields_to_base()
        new_color.save()
        color = new_color
    return color

def save_color(dog, raw_color):
    stripped_color = raw_color.replace(".", " ").replace("`","").strip()
    save_color = stripped_color.replace(",","").replace(" ","").replace("\n","").replace("-","")

    if len(save_color) > 0:
        if save_color.isalpha():
            color = get_color(save_color)
            dog.color = color
            dog.save()
        else:
            print("Non alpha characters detected for color:")
            print(save_color)

def save_sex(dog, raw_sex):
    if raw_sex.strip():
        sex = raw_sex.strip().upper()[0]
        if sex in ['M', 'F']:
            dog.sex = sex
            dog.save()
        else:
            print("Sex Not Found!")
            print("{}{}".format(dog_root, dog.name.replace(" ", "+")))
