import datetime

from django.db import models

from derbylane.applib.models import CoreModel


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
        ordering = ['name']
        verbose_name = 'Venue'

    name = models.CharField(
        null=True,
        max_length=128)
    code = models.CharField(
        max_length=128)
    is_active = models.BooleanField(default=True)
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
    weatherlookup = models.ForeignKey(
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
    whelp_date = models.DateField(null=True)
    sex = models.CharField(
        null=True,
        max_length=1,
        choices=SEX_CHOICES
    )
    color = models.ForeignKey(
        Color,
        null=True,
        on_delete=models.CASCADE)
    kennel = models.CharField(
        null=True,
        max_length=128)
    sire = models.ForeignKey(
        'self',
        related_name='father',
        null=True,
        on_delete=models.CASCADE)
    dam = models.ForeignKey(
        'self',
        related_name='mother',
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
    last_scanned = models.DateTimeField(null=True)

    def get_litters(self):
        if self.sex is 'F':
            return Litter.objects.filter(dam=self)
        elif self.sex is 'M':
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

    url = models.ForeignKey(
        Url,
        null=True,
        on_delete=models.CASCADE)
    program = models.ForeignKey(
        Program,
        null=True,
        on_delete=models.CASCADE)

    time = models.CharField(
        max_length=128,
        choices=TIME_CHOICES
    )
    is_cancelled = models.BooleanField(default=False)

class Grade(CoreModel):

    name = models.CharField(
        null=True,
        max_length=3
    )
    value = models.IntegerField(
        null=True
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
    condition = models.CharField(
        max_length=1,
        choices=CONDITION_CHOICES,
        null=True
    )
    legacy_grade = models.CharField(
        null=True,
        max_length=3,
        choices=GRADE_CHOICES
    )
    grade = models.ForeignKey(
        Grade,
        null=True,
        on_delete=models.CASCADE)
    is_training = models.BooleanField(default=False)
    distance = models.IntegerField(
        choices=DISTANCE_CHOICES,
        null=True)
    winning_time = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True
    )

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




class Participant(CoreModel):

    class Meta:
        verbose_name = 'Participant'
        ordering = ['final', 'post']

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
        max_digits=4,
        decimal_places=2,
        null=True
    )
    actual_running_time = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True
    )
    comment = models.CharField(
        null=True,
        max_length=256)


class BetType(CoreModel):
    class Meta:
        verbose_name = 'BetType'

    name = models.CharField(
        max_length=64
    )


class Payout(CoreModel):

    class Meta:
        abstract = True

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True)
    type = models.ForeignKey(
        BetType,
        on_delete=models.CASCADE,
        null=True)

class Combination(Payout):

    class Meta:
        verbose_name = 'CombinationPayout'

    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        null=True
    )


class Single(Payout):

    class Meta:
        verbose_name = 'DogPayout'

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        null=True
    )

class HistoryScan(CoreModel):

    class Meta:
        verbose_name = 'HistoryScan'

    complete = models.BooleanField(default=False)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
