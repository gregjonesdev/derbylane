from django.core.exceptions import ObjectDoesNotExist
from rawdat.models import (
    Color,
    Chart,
    Program,
    Race,
    Participant,
    Quiniela,
    Exacta,
    Trifecta,
    Superfecta,
    # BetType,
    Grade,
    Straight_Wager,
    Dog,
    Litter
)

from miner.utilities.constants import (
    race_conditions,
    cost,
    grade_skips,
    distance_converter
)

from miner.utilities.common import (
    get_node_elements,
)

from miner.utilities.urls import (
    build_dog_profile_url,
)



def create_quiniela(race, posts, cost, payout):
    print("create quin")
    if posts[0].isnumeric() and posts[1].isnumeric():
        print("{} is numeric".format(posts[0]))
        print("{} is numeric".format(posts[1]))
        entrants = [
            get_participant_from_post(race, int(posts[0])),
            get_participant_from_post(race, int(posts[1]))
            ]
        try:
            bet = Quiniela.objects.get(
                race=race,
                left__in=entrants,
                right__in=entrants
            )
        except ObjectDoesNotExist:
            new_bet = Quiniela(
                race=race,
                left=entrants[0],
                right=entrants[1]
            )
            new_bet.set_fields_to_base()
            bet = new_bet
        if cost:
            bet.cost = cost
        if payout:
            bet.payout = payout
        bet.save()


def get_participant_from_post(race, post):
    # print(race)
    # print(post)
    try:
        return Participant.objects.get(
            race=race,
            post=int(post)
        )
    except:
        print("Error get part from post")
        raise SystemExit(0)


def create_exacta(race, posts, cost, payout):
    print("create exacta")
    if posts[0].isnumeric() and posts[1].isnumeric():
        win = get_participant_from_post(race, int(posts[0]))
        place = get_participant_from_post(race, int(posts[1]))
        try:
            bet = Exacta.objects.get(
                race=race,
                win=win,
                place=place,
            )
        except ObjectDoesNotExist:
            new_bet = Exacta(
                race=race,
                win=win,
                place=place,
            )
            new_bet.set_fields_to_base()
            bet = new_bet
        if cost:
            bet.cost = cost
        if payout:
            bet.payout = payout
        bet.save()




def create_trifecta(race, posts, cost, payout):
    if posts[0].isnumeric() and posts[1].isnumeric() and posts[2].isnumeric():
        win = get_participant_from_post(race, int(posts[0]))
        place = get_participant_from_post(race, int(posts[1]))
        show = get_participant_from_post(race, int(posts[2]))
        try:
            bet = Trifecta.objects.get(
                race=race,
                win=win,
                place=place,
                show=show
            )
        except ObjectDoesNotExist:
            new_bet = Trifecta(
                race=race,
                win=win,
                place=place,
                show=show
            )
            new_bet.set_fields_to_base()
            bet = new_bet
        if cost:
            bet.cost = cost
        if payout:
            bet.payout = payout
        bet.save()

def create_superfecta(race, posts, cost, payout):
    if posts[0].isnumeric() and posts[1].isnumeric() and posts[2].isnumeric() and posts[3].isnumeric():
        win = get_participant_from_post(race, int(posts[0]))
        place = get_participant_from_post(race, int(posts[1]))
        show = get_participant_from_post(race, int(posts[2]))
        take = get_participant_from_post(race, int(posts[3]))
        try:
            bet = Superfecta.objects.get(
                race=race,
                win=win,
                place=place,
                show=show,
                take=take
            )
        except ObjectDoesNotExist:
            new_bet = Superfecta(
                race=race,
                win=win,
                place=place,
                show=show,
                take=take
            )
            new_bet.set_fields_to_base()
            bet = new_bet
        if cost:
            bet.cost = cost
        if payout:
            bet.payout = payout
        bet.save()


def get_parent_name(url, class_attr):
    # print(url)
    return get_node_elements(
        url,'//td[@class="{}"]//a'.format(class_attr))[0].text


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



def save_dog_info(dog):
    url = build_dog_profile_url(dog.name)
    # print(url)
    if not dog.litter:
        whelp_date = get_node_elements(url, '//td[@class="it4"]//em')[0].text
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
    # print(name)
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

def get_grade(raw_grade):
    stripped_grade = raw_grade.strip().upper()
    if stripped_grade:
        if stripped_grade in grade_skips:
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
        return None

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
    # print(participant.dog.name)
    # print(post_weight)
    # print(post)
    # print(off)
    # print(eighth)
    # print(straight)
    # print(final)
    # print(actual_running_time)
    # print(lengths_behind)
    # print(comment)

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
        participant.lengths_behind = lengths_behind
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

def save_race_info(race, raw_setting):
    if raw_setting:
        for item in raw_setting[:3]:
            if is_grade(item):
                race.grade = get_grade(item)
        for item in raw_setting:
            if item in distance_converter:
                item = distance_converter[item]
            try:
                item = int(item)
                if 100 < item < 900:
                    distance = int(item)
                    race.distance = distance
            except:
                pass
        for item in raw_setting[3:]:
            if item.upper() in race_conditions:
                race.condition = item.upper()
        race.save()

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
    # print("SELECT * FROM rawdat_participant WHERE race_id='{}' and dog_id='{}'".format(race.uuid, dog.uuid))
    # for part in Participant.objects.filter(
    #     race=race,
    #     dog=dog):
    #     print(part.uuid)

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

def save_sex_and_color(dog, elements):
    try:
        text = elements[0].text
        sex_and_color = text.split("/")
        save_sex(dog, sex_and_color[0])
        save_color(dog, sex_and_color[1])
    except:
        pass


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
