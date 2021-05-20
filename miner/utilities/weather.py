import requests
from datetime import date, datetime
from django.core.exceptions import ObjectDoesNotExist
from rawdat.models import (
    Program,
    Weather
)
from bs4 import BeautifulSoup
import time
from miner.utilities.common import get_node_elements, force_date
from miner.utilities.urls import (
    build_almanac_url,
    build_forecast_url,)
from miner.utilities.constants import (
    days_of_week,
    user_agent)


def build_weather_from_forecast(program):
    print("FAWK YEAH")
    if not Weather.objects.filter(program=program).count():
        program_date = force_date(program.date)
        index = program_date.weekday()
        target_day = days_of_week[index]
        r = requests.get(build_forecast_url(program))
        data = r.json()
        day_index = get_day_index(data["dayOfWeek"], target_day)
        daypart = data["daypart"][0]

        if daypart:
            try:
                max_temp = get_offset_index(day_index, data["calendarDayTemperatureMax"], 0)
            except:
                max_temp = None
            try:
                min_temp = get_offset_index(day_index, data["calendarDayTemperatureMin"], 1)
            except:
                min_temp = None
            try:
                percipitation = get_daynight_index(day_index, daypart["precipChance"])
            except:
                percipitation = None
            try:
                mean_rh = get_daynight_index(day_index, daypart["relativeHumidity"])/100
            except:
                mean_rh = None
            try:
                wind = get_daynight_index(day_index, daypart['windSpeed'])
            except:
                wind = None


            weather_instance = get_weatherinstance(program)
            update_weather(
                weather_instance,
                None,
                min_temp,
                None,
                max_temp,
                mean_rh,
                None,
                None,
                percipitation,
                None,
                wind)

def get_nightly_index(day_index, list):
    return list[day_index*2 + 1]

def get_daynight_index(day_index, list):
    return list[day_index*2]

def get_offset_index(day_index, list, offset):
    return list[day_index+1]

def get_day_index(days, target_day):
    return days.index(target_day)


def build_weather_from_almanac(program):

    headers = {'User-Agent': user_agent}
    response = requests.get(
        build_almanac_url(program),
        headers=headers)
    html_text = response.text
    soup = BeautifulSoup(html_text, 'html.parser')
    process_rows(program, soup)

def process_rows(program, soup):
    rows = soup.select('tr')

    weather_data = []
    min_temp = is_temp(get_value(rows, 'temp_mn'))
    mean_temp = is_temp(get_value(rows, 'temp'))
    max_temp = is_temp(get_value(rows, 'temp_mx'))
    pressure = is_pressure(get_value(rows, 'slp'))
    dew_point = is_temp(get_value(rows, 'dewp'))
    percipitation = is_percipitation(get_value(rows, 'prcp'))
    visibility = is_visibility(get_value(rows, 'visib'))
    wind = is_wind(get_value(rows, 'wdsp'))
    max_rh = None
    mean_rh = None
    try:
        max_rh = get_rh(float(max_temp), float(dew_point))
        mean_rh = get_rh(float(mean_temp), float(dew_point))
    except TypeError:
        pass

    print(max_rh)
    print(mean_rh)
    raise SystemExit(0)
    weather_instance = get_weatherinstance(program)
    update_weather(
        weather_instance,
        dew_point,
        min_temp,
        mean_temp,
        max_temp,
        mean_rh,
        max_rh,
        pressure,
        percipitation,
        visibility,
        wind)


def get_weatherinstance(program):
    try:
        weather = Weather.objects.get(program=program)
    except ObjectDoesNotExist:
        new_weather = Weather(
            program=program)
        new_weather.set_fields_to_base()
        new_weather.save()
        weather = new_weather
    return weather


def update_weather(
    weather_instance,
    dew_point,
    min_temp,
    mean_temp,
    max_temp,
    mean_rh,
    max_rh,
    pressure,
    percipitation,
    visibility,
    wind):
    if dew_point:
        weather_instance.dew_point = dew_point
    if min_temp:
        weather_instance.min_temp = min_temp
    if mean_temp:
        weather_instance.mean_temp = mean_temp
    if max_temp:
        weather_instance.max_temp = max_temp
    if mean_rh:
        weather_instance.mean_rh = mean_rh
    if max_rh:
        weather_instance.max_rh = max_rh
    if pressure:
        weather_instance.pressure = pressure
    if percipitation:
        weather_instance.percipitation = percipitation
    if visibility:
        weather_instance.visibility = visibility
    if wind:
        weather_instance.wind = wind
    weather_instance.save()


def get_value(rows, target_attr):
    for row in rows:
        if target_attr in row.get('class'):
            spans = row.select('span')
            for span in spans:
                span_class_attr = span.get('class')
                if span_class_attr and 'value' in span_class_attr:
                    return span.contents[0]


def is_wind(num):
    if num:
        if 0<=float(num)<=75:
            return num
        else:
            print("Not wind: {}".format(num))
            return float(input("Enter correct value: "))

def is_visibility(num):
    if num:
        if 0<=float(num)<=10:
            return num
        else:
            print("Not visibility: {}".format(num))
            return float(input("Enter correct value: "))

def is_percipitation(num):
    if num:
        if 0<=float(num)<=71:
            return num
        else:
            print("Not a parcipitation: {}".format(num))
            return float(input("Enter correct value: "))
#
# def is_relhumid(num):
#     if num:
#         if 0<=float(num)<=100:
#             return num
#         else:
#             print("Not a relative humidity: {}".format(num))
#             return float(input("Enter correct value: "))

def is_pressure(num):
    if num:
        if 29<float(num)<33:
            return num
        else:
            print("Not a pressure: {}".format(num))
            return float(input("Enter correct value: "))

def is_temp(num):
    if num:
        if -20<float(num)<120:
            return num
        else:
            print("Not a temperature: {}".format(num))
            return float(input("Enter correct value: "))

def get_rh(tempf, dew_tempf):
    if tempf and dew_tempf:
        tempc = f_to_c(tempf)
        dew_tempc = f_to_c(dew_tempf)
        good=6.11*10.0**(7.5*dew_tempc/(237.7+dew_tempc))
        dog=6.11*10.0**(7.5*tempc/(237.7+tempc))
        return (good/dog)


def f_to_c(tempf):
    return 5*(tempf-32)/9
