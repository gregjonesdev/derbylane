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
    Bet,
    Straight_Wager,
    StraightBetType)


from pww.models import Participant_Prediction

class Command(BaseCommand):

    def change_bets(self, bets):
        for bet in bets:
            try:
                sizzle = Straight_Bet.objects.get(
                    participant=bet.participant,
                    type=bet.type
                )
            except ObjectDoesNotExist:
                print("DNE")
                sizzle = Straight_Bet(
                    participant=bet.participant,
                    type=bet.type,
                    purchase_amount=bet.amount,
                    payout=bet.get_return()
                )
                sizzle.set_fields_to_base()
                sizzle.save()
        print(Straight_Bet.objects.all().count())

    def change_straight_wagers(self, wagers):
        win_count = 0
        place_count = 0
        show_count = 0
        for wager in wagers:
            win_payout = 0
            place_payout = 0
            show_payout = 0
            if wager.win:
                win_payout = wager.win
            if wager.place:
                place_payout = wager.place
            if wager.show:
                show_payout = wager.show
            try:
                win_sizzle = Straight_Bet.objects.get(
                    participant=wager.participant,
                    type=StraightBetType.objects.get(name="W")
                )
            except ObjectDoesNotExist:
                win_sizzle = Straight_Bet(
                    participant=wager.participant,
                    type=StraightBetType.objects.get(name="W")
                )
            win_sizzle.payout = win_payout
            win_sizzle.set_fields_to_base()
            win_sizzle.save()

            try:
                place_sizzle = Straight_Bet.objects.get(
                    participant=wager.participant,
                    type=StraightBetType.objects.get(name="P")
                )
            except ObjectDoesNotExist:
                place_sizzle = Straight_Bet(
                    participant=wager.participant,
                    type=StraightBetType.objects.get(name="P")
                )
            place_sizzle.payout = place_payout
            place_sizzle.set_fields_to_base()
            place_sizzle.save()



            try:
                show_sizzle = Straight_Bet.objects.get(
                    participant=wager.participant,
                    type=StraightBetType.objects.get(name="S")
                )
            except ObjectDoesNotExist:
                show_sizzle = Straight_Bet(
                    participant=wager.participant,
                    type=StraightBetType.objects.get(name="S")
                )
            show_sizzle.payout = show_payout
            show_sizzle.set_fields_to_base()
            show_sizzle.save()



    def change_quinellas(self, quinellas):
        for quinella in quinellas:
            race = quinella.left.race
            payout = quinella.payout
            try:
                sizzle = Sizzle_Quinella.objects.get(
                    race = race,
                    left = quinella.left,
                    right = quinella.right
                )
            except ObjectDoesNotExist:
                try:
                    sizzle = Sizzle_Quinella.objects.get(
                        race = race,
                        left = quinella.right,
                        right = quinella.left
                    )
                except ObjectDoesNotExist:
                    new_sizzle = Sizzle_Quinella(
                        race = race,
                        left = quinella.left,
                        right = quinella.right,
                        payout = payout
                    )
                    new_sizzle.set_fields_to_base()
                    new_sizzle.save()
        print(Sizzle_Quinella.objects.all().count())

    def change_exactas(self, exactas):
        for exacta in exactas:
            race = exacta.win.race
            payout = exacta.payout
            try:
                sizzle = Sizzle_Exacta.objects.get(
                    race = race,
                    win = exacta.win,
                    place = exacta.place
                )
            except ObjectDoesNotExist:
                new_sizzle = Sizzle_Exacta(
                    race = race,
                    win = exacta.win,
                    place = exacta.place,
                    payout = payout
                )
                new_sizzle.set_fields_to_base()
                new_sizzle.save()
        print(Sizzle_Exacta.objects.all().count())

    def change_trifectas(self, trifectas):
        for trifecta in trifectas:
            race = trifecta.win.race
            payout = trifecta.payout
            try:
                sizzle = Sizzle_Trifecta.objects.get(
                    race = race,
                    win = trifecta.win,
                    place = trifecta.place,
                    show = trifecta.show
                )
            except ObjectDoesNotExist:
                new_sizzle = Sizzle_Trifecta(
                    race = race,
                    win = trifecta.win,
                    place = trifecta.place,
                    show = trifecta.show,
                    payout = payout
                )
                new_sizzle.set_fields_to_base()
                new_sizzle.save()
        print(Sizzle_Trifecta.objects.all().count())



    def handle(self, *args, **options):
        print(Quiniela.objects.all().count())
        self.change_quinellas(Quiniela.objects.all())
        print(Exacta.objects.all().count())
        self.change_exactas(Exacta.objects.all())
        print(OldTrifecta.objects.all().count())
        self.change_trifectas(OldTrifecta.objects.all())
        print(Bet.objects.all().count())
        self.change_bets(Bet.objects.all())
        self.change_straight_wagers(Straight_Wager.objects.all())
        # print(Superfecta.objects.all().count())
        # print(Straight_Wager.objects.all().count())
        # print(Participant_Prediction.objects.all().count())
