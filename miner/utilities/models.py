from django.core.exceptions import ObjectDoesNotExist
from rawdat.models import (
    Color,
    Chart,
    Program,
    Race,
    Participant,
    Combination,
    BetType,
    Grade,
    Single,
    Dog,
    Litter
)

from miner.utilities.constants import (
    race_conditions,
    cost,
    grade_skips,
    distance_converter
)

from miner.utilities.common import get_node_elements

from miner.utilities.urls import (
    dog_root,
)


def save_dog_info(dog):
    url = "{}{}".format(dog_root, dog.name.replace(" ", "+"))
    try:
        sire = get_dog(get_node_elements(url, '//td[@class="it2"]//a')[0].text)
        dam = get_dog(get_node_elements(url, '//td[@class="it4"]//a')[0].text)
        whelp_date = get_node_elements(url, '//td[@class="it4"]//em')[0].text
        # whelp_date = datetime.datetime.strptime(raw_date,'%Y-%m-%d')
        if sire and dam and whelp_date:
            litter = get_litter(sire, dam, whelp_date)
            dog.litter = litter
            dog.save()
            save_sex_and_color(
            dog,
            get_node_elements(url, '//td[@class="it2"]//em'))
    except:
        pass



def get_dog(name):
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

def create_single(participant, type, amount):
    try:
        single = Single.objects.get(
            participant=participant,
            type=type
        )
    except ObjectDoesNotExist:
        new_single = Single(
            participant=participant,
            type=type,
            cost=cost,
            amount=amount
        )
        new_single.set_fields_to_base()
        new_single.save()

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

def create_combination(race, cost, type, amount):
    try:
        combination = Combination.objects.get(
            race=race,
            type=type
        )
    except ObjectDoesNotExist:
        new_combination = Combination(
            race=race,
            type=type,
            cost=cost,
            amount=amount
        )
        new_combination.set_fields_to_base()
        new_combination.save()

def save_sex_and_color(dog, elements):
    try:
        text = elements[0].text
    except:
        print("Error saving sex and color")
        print(dog.name)
        for element in elements:
            print(element.text)
    sex_and_color = text.split("/")
    save_sex(dog, sex_and_color[0])
    save_color(dog, sex_and_color[1])


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

def get_bettype(name):
    name = name.upper()
    try:
        bettype = BetType.objects.get(name=name)
    except ObjectDoesNotExist:
        new_bettype = BetType(
            name=name
        )
        new_bettype.set_fields_to_base()
        new_bettype.save()
        bettype = new_bettype
    return bettype