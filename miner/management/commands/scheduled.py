import datetime

from django.core.management.base import BaseCommand

from rawdat.models import (
    Program,
    Venue,
    )

from miner.utilities.scrape import build_daily_charts

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Scheduled script..")
        dates = self.get_dates()
        for venue in Venue.objects.filter(is_active=True):
            for date in dates:
                # build_daily_charts(venue, date.year, date.month, date.day)
                self.get_forecast(venue.weatherlookup.geocode, date)
                # race data

    def get_forecast(self, geocode, date):
        self.stdout.write("geocode: {}".format(geocode))
        self.stdout.write("date: {}".format(date))

    def get_dates(self):
        dates = []
        i = 0
        while i < 3:
            offset = datetime.timedelta(days=i)
            dates.append(datetime.datetime.now() + offset)
            i += 1
        return dates
