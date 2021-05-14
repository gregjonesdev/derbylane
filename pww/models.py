from django.db import models

from derbylane.applib.models import CoreModel

from rawdat.models import Race, Participant

class Metric(CoreModel):

    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    scaled_fastest_time = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    win = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    place = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    show = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    break_avg = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    eighth_avg = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    straight_avg = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    finish_avg = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    grade_avg = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    time_seven = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    time_three = models.DecimalField(
        max_digits=8,
        decimal_places=8,
    )
    upgrade = models.IntegerField()
    # age
    # sex
    # post_weight_avg
    # post_factor
    # temp_factor
    # rh_factor

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
