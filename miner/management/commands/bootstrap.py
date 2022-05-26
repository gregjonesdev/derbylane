import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rawdat.models import (
    Venue,
    Grade,
    StraightBetType)

from pww.models import BettingGrade, WekaClassifier, WekaModel

class Command(BaseCommand):

    def handle(self, *args, **options):

        self.stdout.write("Starting Bootstrap script..\n")
        jsonData = json.loads(open('./rawdat/json/data.json').read())
        wekaData = json.loads(open('./rawdat/json/weka.json').read())
        self.seed_users(jsonData["users"])
        self.seed_venues(jsonData["venues"])
        self.seed_grades(jsonData["race_grades"])
        self.seed_bettypes(jsonData["straight_bet_types"])
        self.seed_betting_grades(wekaData["betting_grades"])
        self.seed_classifiers(wekaData["classifiers"])
        self.seed_models(wekaData["models"])
        self.stdout.write("\nComplete.")

    def build_model(
        self,
        classifier,
        betting_grade,
        training_start,
        training_end):
        try:
            weka_model = WekaModel.objects.get(
                classifier=classifier,
                betting_grade=betting_grade,
                training_start=training_start,
                training_end=training_end
            )
        except ObjectDoesNotExist:
            new_weka_model = WekaModel(
                classifier=classifier,
                betting_grade=betting_grade,
                training_start=training_start,
                training_end=training_end
            )
            new_weka_model.set_fields_to_base()
            new_weka_model.save()


    def seed_models(self, models):
        for model in models:
            classifier = WekaClassifier.objects.get(name=model["classifier"])
            self.stdout.write("Building '{}' Models".format(classifier.name))
            for model_venue in model["venues"]:
                venue = Venue.objects.get(code=model_venue["code"])
                for venue_grade in model_venue["grades"]:
                    grade = Grade.objects.get(name=venue_grade["name"])
                    betting_grade = BettingGrade.objects.get(
                        venue=venue,
                        grade=grade
                    )
                    for date_range in venue_grade["date_ranges"]:
                        self.build_model(
                            classifier,
                            betting_grade,
                            date_range["start_date"],
                            date_range["end_date"])


    def seed_classifiers(self, classifiers):
        self.stdout.write("Building Classifiers")
        for classifier in classifiers:
            try:
                weka_classifier = WekaClassifier.objects.get(
                    name = classifier["name"]
                )
            except ObjectDoesNotExist:
                new_classifier = WekaClassifier(
                    name= classifier["name"],
                )
                new_classifier.set_fields_to_base()
                weka_classifier = new_classifier
            weka_classifier.is_nominal = classifier["is_nominal"]
            weka_classifier.save()

    def seed_betting_grades(self, betting_grades):
        self.stdout.write("Building Betting Grades")
        for betting_grade in betting_grades:
            grade = Grade.objects.get(name=betting_grade["grade_name"])
            venue = Venue.objects.get(code=betting_grade["venue_code"])

            try:
                type = BettingGrade.objects.get(
                    grade = grade,
                    venue = venue
                )
            except ObjectDoesNotExist:
                new_betting_grade = BettingGrade(
                    grade = grade,
                    venue = venue
                )
                new_betting_grade.set_fields_to_base()
                new_betting_grade.save()

    def seed_bettypes(self, bettypes):
        self.stdout.write("Building Bet Types")
        for type in bettypes:
            self.create_bet_type(type["name"], type["cutoff"])

    def create_bet_type(self, name, cutoff):
        try:
            type = StraightBetType.objects.get(name=name)
        except ObjectDoesNotExist:
            new_type = StraightBetType(
                name=name,
                cutoff=cutoff
            )
            new_type.set_fields_to_base()
            new_type.save()


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
        self.stdout.write("Seeding Users")
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
            venue = self.get_venue(venue)

    def get_venue(self, venue):
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
            )

            new_venue.set_fields_to_base()
            new_venue.save()
            venue = new_venue
        return venue
