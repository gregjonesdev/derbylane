import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rawdat.models import (
    Venue,
    WeatherLookup,
    Grade)

class Command(BaseCommand):

    def handle(self, *args, **options):

        self.stdout.write("Starting Bootstrap script..")
        data = open('./rawdat/json/data.json').read()
        jsonData = json.loads(data)
        self.seed_users(jsonData["users"])
        self.seed_venues(jsonData["venues"])
        self.seed_grades(jsonData["race_grades"])
        self.stdout.write("Complete.")

    def seed_grades(self, grades):
        for grade in grades:
            try:
                grade = Grade.objects.get(name=grade["name"])
            except ObjectDoesNotExist:
                new_grade = Grade(
                    name=grade["name"],
                    value=grade["value"]
                )
                new_grade.set_fields_to_base()
                new_grade.save()

    def seed_users(self, users):
        for user in users:
            try:
                user = User.objects.get(username=user["username"])
            except ObjectDoesNotExist:
                user = User(
                    is_superuser=user["is_superuser"],
                    username=user["username"],
                    first_name=user["first_name"],
                    last_name=user["last_name"],
                    is_active=user["is_active"],
                )
                user.save()

    def seed_venues(self, venues):
        for venue in venues:
            weather_lookup = self.get_weatherlookup(venue["weather"])
            venue = self.get_venue(venue, weather_lookup)


    def get_weatherlookup(self, weather):
        try:
            weather_lookup = WeatherLookup.objects.get(
                code=weather['code'],
                )
        except ObjectDoesNotExist:
            weather_lookup = WeatherLookup(
                code=weather['code'],
                place=weather['place'],
                wunderground=weather['wunderground']
            )
        try:
            weather_lookup.geocode = weather['geocode']
        except KeyError:
            pass
        weather_lookup.set_fields_to_base()
        weather_lookup.save()
        return weather_lookup

    def get_venue(self, venue, weather):
        try:
            venue = Venue.objects.get(code=venue['code'])
        except ObjectDoesNotExist:
            new_venue = Venue(
                name=venue['name'],
                code=venue['code'],
                is_active=venue['is_active'],
                city=venue['city'],
                state=venue['state'],
                zip_code=venue['zip_code'],
                country=venue['country'],
                weatherlookup=weather
            )

            new_venue.set_fields_to_base()
            new_venue.save()
            venue = new_venue
        return venue
