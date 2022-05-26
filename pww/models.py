from django.db import models

from derbylane.applib.models import CoreModel

from rawdat.models import Race, Participant, Venue, Grade

class Metric(CoreModel):

    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    scaled_fastest_time = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    win = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    place = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    show = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    break_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    eighth_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    straight_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    finish_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    grade_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
    )
    time_seven = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    time_three = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    upgrade = models.IntegerField()
    final = models.IntegerField(null=True)
    age = models.IntegerField(null=True)
    sex = models.CharField(
        max_length=16,
        null=True
    )
    post_weight_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    post_factor = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    temp_factor = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )
    rh_factor = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True
    )

    def build_csv_metric(self, is_training):
        if is_training:
            final = self.participant.final
        else:
            final = "?"
        post_factor = self.post_factor if self.post_factor else 0.5
        temp_factor = self.temp_factor if self.temp_factor else 0.5
        rh_factor = self.rh_factor if self.rh_factor else 0.5
        age = self.age if self.age else 990 # 33 months
        sex = self.sex if self.sex else "M"
        metric_csv_string = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
            self.participant.uuid,
            self.scaled_fastest_time,
            self.win,
            self.place,
            self.show,
            self.break_avg,
            self.eighth_avg,
            self.straight_avg,
            self.finish_avg,
            self.grade_avg,
            self.time_seven,
            self.time_three,
            self.upgrade,
            age,
            # sex,
            # self.post_weight_avg,
            post_factor,
            # temp_factor,
            # rh_factor,
            final
            )
        if not "None" in metric_csv_string:
            return metric_csv_string


class Prediction(CoreModel):

    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    smoreg = models.DecimalField(
        max_digits=16,
        decimal_places=8,
        null=True)
    bet = models.CharField(
        max_length=16,
        null=True
    )

    def get_bet(self):
        pass


class WekaClassifier(CoreModel):

    name = models.CharField(
        max_length=128)
    is_nominal = models.BooleanField(default=False)

class BettingGrade(CoreModel):

    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE)
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE)


class WekaModel(CoreModel):

    classifier = models.ForeignKey(
        WekaClassifier,
        on_delete=models.CASCADE)
    betting_grade = models.ForeignKey(
        BettingGrade,
        on_delete=models.CASCADE)
    training_start = models.DateField()
    training_end = models.DateField()

    def get_name(self):
        betting_grade = self.betting_grade
        return "{}_{}_{}".format(
            betting_grade.venue.code,
            betting_grade.grade.name,
            str(self.training_start).replace("-", "_"))



class TestPrediction(CoreModel):

    c = models.DecimalField(
        max_digits=16,
        decimal_places=8)
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE)
    smo = models.IntegerField()
