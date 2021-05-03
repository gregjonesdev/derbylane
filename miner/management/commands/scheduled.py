import datetime

from django.core.management.base import BaseCommand

from rawdat.models import (
    Program,
    Venue,
    )

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Scheduled script..")
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        all_scaled_metrics = {}
        for venue in Venue.objects.filter(is_active=True):
            pass
            # self.get_forecast(venue.weatherlookup.geocode, program.date)
            # race data

    def get_forecast(self, geocode, date):
        self.stdout.write("geocode: {}".format(geocode))
        self.stdout.write("date: {}".format(date))
