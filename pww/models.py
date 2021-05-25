from django.db import models

from derbylane.applib.models import CoreModel

from rawdat.models import Race, Participant

class Metric(CoreModel):

    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    scaled_fastest_time = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    win = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    place = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    show = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    break_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    eighth_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    straight_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    finish_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    grade_avg = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    time_seven = models.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    time_three = models.DecimalField(
        max_digits=8,
        decimal_places=4,
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

    def build_csv_metric(self):
        final = self.final if self.final else "?"
        post_factor = self.post_factor if self.post_factor else 0.5
        temp_factor = self.temp_factor if self.temp_factor else 0.5
        rh_factor = self.rh_factor if self.rh_factor else 0.5
        age = self.age if self.age else 990 # 33 months
        sex = self.sex if self.sex else "M"
        if self.post_weight_avg:
            return "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
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
                sex,
                self.post_weight_avg,
                post_factor,
                temp_factor,
                rh_factor,
                final)




class Prediction(CoreModel):

    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    j48 = models.DecimalField(
            max_digits=8,
            decimal_places=8,
        )
    smo = models.DecimalField(
            max_digits=8,
            decimal_places=8,
            )
    lib_linear = models.DecimalField(
            max_digits=8,
            decimal_places=8,
            )
    lib_svm = models.DecimalField(
            max_digits=8,
            decimal_places=8,
            )
    smo_reg = models.DecimalField(
            max_digits=8,
            decimal_places=8,
            )
