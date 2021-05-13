import datetime

from django.core.management.base import BaseCommand
from miner.utilities.models import get_program
from miner.utilities.scrape import scan_scheduled_charts
from miner.utilities.weather import build_weather_from_forecast
from rawdat.models import Program, Venue

from rawdat.utilities.methods import get_date_from_ymd

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Scheduled script..")
        dates = self.get_dates()
        for venue in Venue.objects.filter(is_active=True):
            print("Processing {}".format(venue.name))
            for date in dates:
                formatted_date = get_date_from_ymd(
                    date.year,
                    date.month,
                    date.day)
                program = get_program(
                    venue,
                    formatted_date)
                build_weather_from_forecast(program)
                print("Scanning {}/{} Charts".format(date.month, date.day))
                scan_scheduled_charts(venue, program)

    def get_dates(self):
        dates = []
        i = 0
        while i < 2:
            offset = datetime.timedelta(days=i)
            dates.append(datetime.datetime.now() + offset)
            i += 1
        return dates
