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

    def build_csv_metric(self, start_date):
        print(start_date)
        print(type(start_date))
        print(self.participant.race.chart.program.date >= start_date)
        print(self.participant.race.chart.program.date < start_date)
        if self.participant.race.chart.program.date >= start_date:
            print("inc")
            final = "?"
        else:
            final = self.participant.final
        post_factor = self.post_factor if self.post_factor else 0.5
        temp_factor = self.temp_factor if self.temp_factor else 0.5
        rh_factor = self.rh_factor if self.rh_factor else 0.5
        age = self.age if self.age else 990 # 33 months
        sex = self.sex if self.sex else "M"
        if self.post_weight_avg:
            metric_csv_string = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
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
                # temp_factor,
                # rh_factor,
                final)
            if not "None" in metric_csv_string:
                return metric_csv_string
            else:
                print(metric_csv_string)


class Bet_Margin(CoreModel):

    venue =  models.ForeignKey(
        Venue,
        on_delete=models.CASCADE)
    distance = models.IntegerField()
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE)
    prediction = models.DecimalField(
            max_digits=16,
            decimal_places=1,
            null=True
        )
    win = models.DecimalField(
            max_digits=16,
            decimal_places=2,
            null=True
        )
    place = models.DecimalField(
            max_digits=16,
            decimal_places=2,
            null=True
        )
    show = models.DecimalField(
            max_digits=16,
            decimal_places=2,
            null=True
        )




class Prediction(CoreModel):

    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    j48 = models.IntegerField(
            null=True)
    smo = models.DecimalField(
            max_digits=16,
            decimal_places=8,
            null=True
            )
    lib_linear = models.DecimalField(
            max_digits=16,
            decimal_places=8,
            null=True
            )
    lib_svm = models.IntegerField(
            null=True)
    smo_reg = models.DecimalField(
            max_digits=16,
            decimal_places=8,
            null=True
            )

    def get_bets(self):
        if self.lib_svm == 1:
            return "P"
        # if self.j48 == 2:
        #     return "S"
        # elif self.j48 == 1:
        #     return "PS"


class TestPrediction(CoreModel):

    c = models.DecimalField(
        max_digits=16,
        decimal_places=8)
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE)
    smo = models.IntegerField()
