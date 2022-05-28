from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rawdat.models import (
    Race,
    Condition,
    Grade)


from pww.models import Participant_Prediction

class Command(BaseCommand):


    def handle(self, *args, **options):

        for race in Race.objects.all():
            try:
                condition = Condition.objects.get(name=race.legacy_condition)
            except ObjectDoesNotExist:
                new_condition = Condition(
                    name=race.legacy_condition
                )
                new_condition.set_fields_to_base()
                new_condition.save()
                condition = new_condition

            try:
                grade = Grade.objects.get(name=race.legacy_grade)
            except ObjectDoesNotExist:
                new_grade = Grade(
                    name=race.legacy_grade
                )
                new_grade.set_fields_to_base()
                new_grade.save()
                grade = new_grade

            race.condition = condition
            race.grade = grade
            race.save()
