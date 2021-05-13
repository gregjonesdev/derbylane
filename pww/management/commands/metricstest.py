

from django.core.management.base import BaseCommand
from rawdat.models import Race

from pww.utilities.metrics import calculate_scaled_race_metrics

from scipy.optimize import curve_fit
from numpy import arange

def objective(x, a, b, c, d):
    return a*x + b*x**2 + c*x**3 + d


class Command(BaseCommand):

    def handle(self, *args, **options):

        # races = Race.objects.filter(chart__program__date="2021-05-13", chart__program__venue__code="WD")[:1]
        # print(races)
        # calculate_scaled_race_metrics(races[0])

        x_values = [1, 2, 3, 5, 6]
        y_values = [2, 4, 6, 10, 12]

        popt, _ = curve_fit(objective, x_values, y_values)

        a, b, c, d = popt
        y = objective(4, float(a), float(b), float(c), float(d))
        print(y)
        # print(a)
        # print(b)
        # print(c)
        # print('y = %.5f * x + %.5f * x^2 + %.5f' % (a, b, c))











# from pandas import read_csv
# from scipy.optimize import curve_fit
# from matplotlib import pyplot
#
# def objective(x, a, b, c):
# 	return a * x + b * x**2 + c
#
# # load the dataset
# dataframe = read_csv(url, header=None)
# data = dataframe.values
# # choose the input and output variables
# x, y = data[:, 4], data[:, -1]
# # curve fit
# popt, _ = curve_fit(objective, x, y)
# # summarize the parameter values
# a, b, c = popt
# print('y = %.5f * x + %.5f * x^2 + %.5f' % (a, b, c))
# # plot input vs output
# # pyplot.scatter(x, y)
# # define a sequence of inputs between the smallest and largest known inputs
# x_line = arange(min(x), max(x), 1)
# # calculate the output for the range
# y_line = objective(x_line, a, b, c)
