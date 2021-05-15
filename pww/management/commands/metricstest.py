

from django.core.management.base import BaseCommand
from rawdat.models import Race

from pww.utilities.metrics import calculate_scaled_race_metrics


class Command(BaseCommand):


    def create_set(self, number):
        master_set = []
        start = 1
        length = 0
        groups = 1
        i = 0
        current_set = []
        while i < number*2:
            j = 0
            while len(current_set) <= length:
                current_set.append(start)
                start += 1
                j +=1
            master_set.append(current_set)
            current_set = []
            length += 1
            i += 1
        return master_set


    def calculate(self, number, set):
        sum = 0
        i = 0
        while i < number:
            running_sum = 0
            for each in set[i*2]:
                running_sum += each
            sum += running_sum
            i += 1
        return sum

    def handle(self, *args, **options):
        # highest_number = 200
        #
        # set = self.create_set(highest_number)
        # # list = [(1,2), (3,4)]
        # # for each in list:
        # #     print(each[0])
        # print("{}\t{}\t\t{}".format("x", "x^4", "Groupings"  ))
        # print("------------------------------------------")
        # i = 1
        # while i < highest_number:
        #     # self.calculate(50)
        #     print("{}\t{}\t\t{}".format(i, i**4, self.calculate(i, set)))
        #     i += 1
        #
        # raise SystemExit(0)
        #
        #
        #


        races = Race.objects.filter(chart__program__date="2021-04-17", chart__program__venue__code="WD")[:1]
        calculate_scaled_race_metrics(races[0])
