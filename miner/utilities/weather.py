import requests
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from rawdat.models import (
    Program,
    Weather
)
from bs4 import BeautifulSoup
import time
from miner.utilities.common import get_node_elements
from miner.utilities.urls import (
    almanac_root,
    json_suffix,
    base_url,
    api_key)
from miner.utilities.constants import days_of_week


def get_forecast_url(program):
    prog_date = program.date
    new_date = date(prog_date.year, prog_date.month, prog_date.day)
    index = new_date.weekday()
    target_day = days_of_week[index]
    target_url = "{}{}&geocode={}{}".format(
        base_url,
        api_key,
        program.venue.weatherlookup.geocode,
        json_suffix)
    print(target_url)
    r = requests.get(url = target_url)
    data = r.json()
    day_index = self.get_day_index(data["dayOfWeek"], target_day)
    daypart = data["daypart"][0]

    if daypart:
        try:
            daily_high = get_offset_index(day_index, data["calendarDayTemperatureMax"], 0)
        except:
            daily_high = None
        try:
            daily_low = get_offset_index(day_index, data["calendarDayTemperatureMin"], 1)
        except:
            daily_low = None
        try:
            rain = get_daynight_index(day_index, daypart["precipChance"])
        except:
            rain = None
        try:
            relHumid = get_daynight_index(day_index, daypart["relativeHumidity"])
        except:
            relHumid = None
        try:
            wind = get_daynight_index(day_index, daypart['windSpeed'])
        except:
            wind = None
        save_forecast(program, daily_high, daily_low, rain, relHumid, wind)

def get_nightly_index(day_index, list):
    return list[day_index*2 + 1]

def get_daynight_index(day_index, list):
    return list[day_index*2]

def get_offset_index(day_index, list, offset):
    return list[day_index+1]

def get_day_index(days, target_day):
    return days.index(target_day)


def save_forecast(program, daily_high, daily_low, rain, relHumid, wind):
    try:
            forecast = VenueForecast.objects.get(venue=venue, date=date)
        except ObjectDoesNotExist:
            new_forecast = VenueForecast(
                venue=venue,
                date=date
                )
            new_forecast.set_fields_to_base()
            forecast = new_forecast
        forecast.max_temp = daily_high
        forecast.min_temp = daily_low
        forecast.percipitation = rain
        forecast.rh = relHumid
        forecast.wind = wind
        forecast.nightly_narrative = narrative
        forecast.save()


def save_weather(program, zip_code, date):
    if zip_code == '22024':
        zip_code = '92154' # closest US zip code to caliente
    target_url = "{}{}/{}".format(almanac_root, zip_code, date)
    target_url = "https://www.almanac.com/weather/history/zipcode/92154/2021-05-08"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
    headers = {'User-Agent': user_agent}
    response = requests.get(target_url, headers=headers)
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

    try:
        weather = Weather.objects.get(program=program)
    except ObjectDoesNotExist:
        new_weather = Weather(
            program=program)
        new_weather.set_fields_to_base()
        new_weather.save()
        weather = new_weather

    print("{} / {} / {} / {} / {} / {} / {} / {} / {} / {}".format(
        dew_point,
        min_temp,
        mean_temp,
        max_temp,
        mean_rh,
        max_rh,
        pressure,
        percipitation,
        visibility,
        wind
    ))

    try:
        weather.dew_point = dew_point
        weather.min_temp = min_temp
        weather.mean_temp = mean_temp
        weather.max_temp = max_temp
        weather.mean_rh = mean_rh
        weather.max_rh = max_rh
        weather.pressure = pressure
        weather.percipitation = percipitation
        weather.visibility = visibility
        weather.wind = wind
        weather.save()
    except:
        pass

def shit_weather():
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


def get_weather(program):
    name = name.upper()
    try:
        weather = Weather.objects.get(name=name)
    except ObjectDoesNotExist:
        new_bettype = BetType(
            name=name
        )
        new_bettype.set_fields_to_base()
        new_bettype.save()
        bettype = new_bettype
    return bettype

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

def is_relhumid(num):
    if num:
        if 0<=float(num)<=100:
            return num
        else:
            print("Not a relative humidity: {}".format(num))
            return float(input("Enter correct value: "))

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
