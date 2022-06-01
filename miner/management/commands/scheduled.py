import datetime

from django.core.management.base import BaseCommand
from miner.utilities.common import get_node_elements
from miner.utilities.constants import chart_times
from miner.utilities.models import get_program, get_race, get_chart
from miner.utilities.scrape_entries import process_entries_url, has_entries
from rawdat.models import Program, Venue, CronJob
from miner.utilities.urls import build_entries_url
from rawdat.utilities.methods import get_date_from_ymd

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Scheduled script..")
        dates = self.get_dates()
        for venue in Venue.objects.filter(is_active=True):
            for date in dates:
                formatted_date = get_date_from_ymd(
                    date.year,
                    date.month,
                    date.day)
                program = get_program(
                    venue,
                    formatted_date)
                print("Scanning {} {}/{} Charts".format(
                    venue.name,
                    date.month,
                    date.day))
                self.scan_scheduled_charts(venue, program, date)
        new_job = CronJob(
            type="Scheduled"
        )
        new_job.set_fields_to_base()
        new_job.save()

    def get_dates(self):
        dates = []
        i = 0
        i = -10
        while i < 2:
            offset = datetime.timedelta(days=i)
            dates.append(datetime.datetime.now() + offset)
            i += 1
        return dates

    def scan_scheduled_charts(self, venue, program, program_date):
        for time in chart_times:
            number = 1
            while number <= 30:
                entries_url = build_entries_url(
                    venue.code,
                    program_date.year,
                    program_date.month,
                    program_date.day,
                    time,
                    number)
                if has_entries(entries_url):
                    chart = get_chart(program, time)
                    race = get_race(chart, number)
                    process_entries_url(entries_url, race)
                number +=1
