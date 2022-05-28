from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rawdat.models import (
    OldTrifecta,
    Exacta,
    Superfecta,
    Quiniela,
    Sizzle_Exacta,
    Sizzle_Quinella,
    Sizzle_Trifecta,
    Sizzle_Superfecta,
    Straight_Bet,
    Bet
    Straight_Wager)


from pww.models import Participant_Prediction

class Command(BaseCommand):

    def handle(self, *args, **options):
        print(Quiniela.objects.all().count())
        print(Exacta.objects.all().count())
        print(Trifecta.objects.all().count())
        print(Superfecta.objects.all().count())
        print(Bet.objects.all().count())
        print(Straight_Wager.objects.all().count())
        print(Participant_Prediction.objects.all().count())
