import datetime
import os
from django.db import models

from derbylane.applib.models import CoreModel

from itertools import chain

class WeatherLookup(CoreModel):
    """ Specific to wunderground. """
    wunderground = models.CharField(
        null=True,
        max_length=128)
    """ Specific to weatherwidget.io. """
    code = models.CharField(
        null=True,
        max_length=128)
    place = models.CharField(
        null=True,
        max_length=128)
    geocode = models.CharField(
        null=True,
        max_length=128)

class Venue(CoreModel):

    class Meta:
        ordering = ['-name']
        verbose_name = 'Venue'

    name = models.CharField(
        null=True,
        max_length=128)
    code = models.CharField(
        max_length=128)
    is_active = models.BooleanField(default=False)
    is_focused = models.BooleanField(default=False)
    street_number = models.CharField(
        null=True,
        max_length=128)
    street_name = models.CharField(
        null=True,
        max_length=128)
    street_suffix = models.CharField(
        null=True,
        max_length=128)
    city = models.CharField(
        null=True,
        max_length=128)
    state = models.CharField(
        null=True,
        max_length=2,
    )
    zip_code = models.CharField(
        null=True,
        max_length=24)
    country = models.CharField(
        max_length=3,
        default='USA',
    )
    weatherlookup = models.OneToOneField(
        WeatherLookup,
        on_delete=models.CASCADE,
        null=True
    )
    website = models.CharField(
        null=True,
        max_length=256)
    about = models.TextField(
        null=True
    )
    kiosk_name = models.CharField(
        null=True,
        max_length=24)

    def __str__(self):
        return self.name


class Color(CoreModel):

    class Meta:
        verbose_name = 'Color'
        ordering = ['name']

    name = models.CharField(
        max_length=128)

class ScanType(CoreModel):

    name = models.CharField(
        null=True,
        max_length=256)


class Scan(CoreModel):

    comment = models.CharField(
        null=True,
        max_length=256)
    completed_at = models.DateTimeField(null=True)
    type = models.ForeignKey(
        ScanType,
        null=True,
        on_delete=models.CASCADE)


class Litter(CoreModel):

    whelp_date = models.DateField(null=True)
    sire = models.ForeignKey(
        'dog',
        related_name='litter_sire',
        null=True,
        on_delete=models.CASCADE)
    dam = models.ForeignKey(
        'dog',
        related_name='litter_dam',
        null=True,
        on_delete=models.CASCADE)

    def get_litter(self):
        return Dog.objects.filter(litter=self)


class Dog(CoreModel):

    SEX_CHOICES = (
        ('F', 'FEMALE'),
        ('M', 'MALE')
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Dog'

    name = models.CharField(
        max_length=128)
    sex = models.CharField(
        null=True,
        max_length=1,
        choices=SEX_CHOICES
    )
    color = models.ForeignKey(
        Color,
        null=True,
        on_delete=models.CASCADE)
    litter = models.ForeignKey(
        Litter,
        on_delete=models.CASCADE,
        null=True
    )
    trainer = models.CharField(
        null=True,
        max_length=128)
    set_weight = models.DecimalField(
        null=True,
        max_digits=4,
        decimal_places=2)

    def get_litters(self):
        if self.sex == 'F':
            return Litter.objects.filter(dam=self)
        elif self.sex == 'M':
            return Litter.objects.filter(sire=self)

    def get_absolute_url(self):
        return "/dog/{}/".format(self.uuid)

    def __str__(self):
        return self.name


class Program(CoreModel):

    class Meta:
        verbose_name = 'Program'
        ordering = ['-date']

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    date = models.DateField()

    def get_charts(self):
        return Chart.objects.filter(program=self)

    def get_predicted_charts(self):
        predicted_charts = []
        for chart in self.chart_set.all():
            if chart.has_predictions():
                predicted_charts.append(chart)


class Chart(CoreModel):
    AFTERNOON = 'A'
    EVENING = 'E'
    SCHOOLING = 'S'
    TWILIGHT = 'T'

    TIME_CHOICES = (
        (AFTERNOON, 'Afternoon'),
        (EVENING, 'Evening'),
        (SCHOOLING, 'Schooling'),
        (TWILIGHT, 'Twilight'),
    )

    class Meta:
        verbose_name = 'Chart'
        ordering = ['time']

    program = models.ForeignKey(
        Program,
        null=True,
        on_delete=models.CASCADE)

    time = models.CharField(
        max_length=128,
        choices=TIME_CHOICES
    )
    is_cancelled = models.BooleanField(default=False)


    def kiosk_time(self):
        if self.time == 'A':
            if self.program.venue.code == 'WD':
                return 'Mat'
            else:
                return "Aft"
        elif self.time == 'E':
            return 'Eve'
        elif self.time == 'T':
            return 'Twi'
        else:
            return self.time

    def get_kiosk_name(self):
        return "{}_{}".format(
            self.program.venue.kiosk_name,
            self.kiosk_time())

    def get_rh(self):
        weather = self.program.weather
        if weather:
            max_rh = weather.max_rh
            mean_rh = weather.mean_rh
            try:
                return float(mean_rh)
            except:
                pass

    def get_racetemp(self):
        weather = self.program.weather
        if weather:
            try:
                return float(weather.max_temp)
            except:
                pass

    def get_predicted_races(self):
        predicted_races = []
        for race in self.race_set.all():
            if race.has_predictions():
                predicted_races.append(race)

    def has_predictions(self):
        for race in self.race_set.all():
            if race.has_predictions():
                return True

    def has_bets(self):
        for race in self.race_set.all():
            if race.has_bets():
                return True

    def is_complete(self):
        for race in self.race_set.all():
            if not race.is_complete():
                return False
        return True

class Grade(CoreModel):

    name = models.CharField(
        null=True,
        max_length=3
    )
    value = models.IntegerField(
        null=True
    )

class Condition(CoreModel):

    name = models.CharField(
        null=True,
        max_length=8
    )


class Race(CoreModel):

    FAST = 'F'
    LOOSE = 'L'
    MUDDY = 'M'
    SLOW = 'S'
    WET = 'W'

    GRADE_CHOICES = (
        ('aa', 'AA'),
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ('e', 'E'),
        ('j', 'J'),
        ('m', 'M'),
    )

    CONDITION_CHOICES = (
        (FAST, 'Fast'),
        (LOOSE, 'Loose'),
        (MUDDY, 'Muddy'),
        (SLOW, 'Slow'),
        (WET, 'Wet'),
    )

    DISTANCE_CHOICES = (
        (440, '440'),
        (546, '546'),
        (550, '550'),
        (583, '583'),
        (660, '660'),
    )

    class Meta:
        verbose_name = 'Race'
        ordering = ['number']

    chart = models.ForeignKey(
        Chart,
        null=True,
        on_delete=models.CASCADE)
    number = models.IntegerField(
        null=True
    )
    condition = models.ForeignKey(
        Condition,
        null=True,
        on_delete=models.CASCADE)
    grade = models.ForeignKey(
        Grade,
        null=True,
        on_delete=models.CASCADE)
    is_training = models.BooleanField(default=False)
    distance = models.IntegerField(
        choices=DISTANCE_CHOICES,
        null=True)

    def get_straight_predictions(self):
        predictions = []
        for participant in self.participant_set.all():
            predictions.append("A")
            if participant.get_recommended_bet():
                predictions.append(participant.get_recommended_bet())
        return predictions

    def get_next(self):
        current_number = self.number
        next_number = current_number + 1
        try:
            return Race.objects.get(chart=self.chart, number=next_number)
        except:
            return False

    def get_previous(self):
        current_number = self.number
        next_number = current_number - 1
        try:
            return Race.objects.get(chart=self.chart, number=next_number)
        except:
            return False

    def has_predictions(self):
        if "dev" in os.environ['DJANGO_SETTINGS_MODULE']:
            return True
        for participant in self.participant_set.all():
            try:
                if participant.get_recommended_bet():
                    return True
            except:
                pass

    def count_predictions(self):
        prediction_count = 0
        for participant in self.participant_set.all():
            try:
                if participant.prediction:
                    prediction_count += 1
            except:
                pass
        return prediction_count

    def has_bets(self):
        if "dev" in os.environ['DJANGO_SETTINGS_MODULE']:
            return True
        for participant in self.participant_set.all():
            if participant.bet_set.count() > 0:
                return True

    def get_displayed_participants(self):
        all_participants = self.participant_set.all()
        if "dev" in os.environ['DJANGO_SETTINGS_MODULE']:
            return all_participants
        participant_list=[]
        if self.is_complete():
            for participant in all_participants:
                if participant.get_bets().count():
                    participant_list.append(participant)
        else:
            for participant in all_participants:
                if participant.get_recommended_bet():
                    participant_list.append(participant)
        return participant_list

    def is_complete(self):
        for participant in self.participant_set.all():
            if participant.final:
                return True

    def get_participant(self, post):
        return Participant.objects.get(race=self, post=post)

    def get_exotic_bets(self):
        pass





class StraightBetType(CoreModel):

    PLACE = 'P'
    SHOW = 'S'
    WIN = 'W'


    NAME_CHOICES = (
        (PLACE, 'Place'),
        (SHOW, 'Show'),
        (WIN, 'Win'),
    )

    name = models.CharField(
        max_length=16,
        choices=NAME_CHOICES)
    cutoff = models.IntegerField()






class Participant(CoreModel):

    class Meta:
        verbose_name = 'Participant'
        ordering = ['post']

    dog = models.ForeignKey(
        Dog,
        on_delete=models.CASCADE,
        null=True
    )
    post_weight = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        null=True
    )
    post = models.IntegerField(
        null=True
    )
    off = models.IntegerField(
        null=True
    )
    eighth = models.IntegerField(
        null=True
    )
    straight = models.IntegerField(
        null=True
    )
    final = models.IntegerField(
        null=True
    )
    lengths_behind = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    actual_running_time = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )
    comment = models.CharField(
        null=True,
        max_length=256)

    def get_recommended_bet(self):
        return self.participant_prediction_set.all()[0]


    def get_bets(self):
        return Bet.objects.filter(participant=self)

    def get_win_bet(self):
        return Bet.objects.get(participant=self,type__name="W")

    def get_place_bet(self):
        return Bet.objects.get(participant=self,type__name="P")

    def get_show_bet(self):
        return Bet.objects.get(participant=self,type__name="S")

    def get_purchased_wagers(self):
        wager_list = ""
        for bet in self.get_bets():
            wager_list += bet.type.name
        return (wager_list)


class Sizzle_Bet(CoreModel):

    class Meta:
        abstract = True

    purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True)
    payout = models.DecimalField(
        max_digits=10,
        decimal_places=2)


class Straight_Bet(Sizzle_Bet):

    type = models.ForeignKey(
        StraightBetType,
        on_delete=models.CASCADE)
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE)


class Sizzle_Trifecta(Sizzle_Bet):

    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE)
    win_post = models.IntegerField(
        null=True
    )
    place_post = models.IntegerField(
        null=True
    )
    show_post = models.IntegerField(
        null=True
    )


class Sizzle_Superfecta(Sizzle_Bet):

    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE)
    win_post = models.IntegerField(
        null=True
    )
    place_post = models.IntegerField(
        null=True
    )
    show_post = models.IntegerField(
        null=True
    )
    fourth_post = models.IntegerField(
        null=True
    )


class Sizzle_Quinella(Sizzle_Bet):

    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE)
    left_post = models.IntegerField(
        null=True
    )
    right_post = models.IntegerField(
        null=True
    )


class Sizzle_Exacta(Sizzle_Bet):

    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE)
    win_post = models.IntegerField(
        null=True
    )
    place_post = models.IntegerField(
        null=True
    )
#
#
class Bet(CoreModel):
    participant =  models.ForeignKey(
        Participant,
        on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=2.00)
    type = models.ForeignKey(
        StraightBetType,
        on_delete=models.CASCADE)

    def button_style(self):
        raw_style = "btn btn-sm btn-block btn-outline-{}"
        if self.get_return() > 0:
            return raw_style.format("success")
        return raw_style.format("danger")



    def get_wager(self):
        return "${} {}".format(self.amount, self.type.name)

    def get_return(self):
        final = self.participant.final
        if final and final <= self.type.cutoff:
            if self.type.name == 'P':
                return self.participant.straight_wager.place
            elif self.type.name == 'S':
                return self.participant.straight_wager.show
            elif self.type.name == 'W':
                return self.participant.straight_wager.win
        else:
            return 0

    def get_date(self):
        return self.participant.race.chart.program.date


class Straight_Wager(CoreModel):
    class Meta:
        verbose_name = 'Straight'

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=2.00)
    participant = models.OneToOneField(
        Participant,
        on_delete=models.CASCADE)
    win = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        null=True)
    place = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        null=True)
    show = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        null=True)


class Winning_Trifecta(CoreModel):

    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE)
    payout = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True)
    win = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='new_trifecta_wager_win')
    place = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='new_trifecta_wager_place')
    show = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='new_trifecta_wager_show')


class Combo(CoreModel):

    class Meta:
        abstract = True

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=2.00)
    payout = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True)
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE)

class Quiniela(Combo):

    class Meta:
        verbose_name = 'Quiniela'

    left = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='quiniela_left')
    right = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='quiniela_right')


class Quiniela_Wager(CoreModel):

    class Meta:
        verbose_name = 'Quinella'

    left = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='quiniela_wager_left')
    right = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='quiniela_wager_right')
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='quiniela_wager')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=2.00)

    def get_name(self):
        return "Quinella"

    def get_posts(self):
        return "{}, {}".format(self.left.post, self.right.post)

class Exacta(Combo):

    class Meta:
        verbose_name = 'Exacta'

    win = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='exacta_win')
    place = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='exacta_place')

class OldTrifecta(Combo):

    class Meta:
        verbose_name = 'Trifecta'

    win = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='trifecta_win')
    place = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='trifecta_place')
    show = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='trifecta_show')

class Superfecta(Combo):

    class Meta:
        verbose_name = 'Superfecta'

    win = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='superfecta_win')
    place = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='superfecta_place')
    show = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='superfecta_show')
    take = models.ForeignKey(
            Participant,
            on_delete=models.CASCADE,
            related_name='superfecta_take')


class Weather(CoreModel):

    program = models.OneToOneField(Program, on_delete=models.CASCADE, null=True)
    dew_point = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )
    min_temp = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )
    mean_temp = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )
    max_temp = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )
    mean_rh = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )
    max_rh = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )
    pressure = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )
    percipitation = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )
    visibility = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )
    wind = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True
    )



class VenueScan(CoreModel):

    class Meta:
        verbose_name = 'VenueScan'

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()


class ScannedUrl(CoreModel):

    class Meta:
        verbose_name = 'ScannedUrl'

    address = models.CharField(
        max_length=256)
    completed = models.BooleanField(default=False)
    comment = models.CharField(
        max_length=256,
        null=True)


class CronJob(CoreModel):

    class Meta:
        verbose_name = 'CronJob'
        ordering = ['-created_at']

    type = models.CharField(
        null=True,
        max_length=256)
#
# class Exotic_Scan(CoreModel):
#
#     start = models.DecimalField(
#         max_digits=8,
#         decimal_places=6,
#         null=True
#     )
#     grade = models.ForeignKey(
#         Grade,
#         null=True,
#         on_delete=models.CASCADE)
#     venue = models.ForeignKey(
#         Venue,
#         null=True,
#         on_delete=models.CASCADE)
