import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.core.management.base import BaseCommand

from miner.utilities.common import get_node_elements
from miner.utilities.scrape import parse_results_url
from miner.utilities.urls import build_race_results_url
from rawdat.models import Race, CronJob
from pww.models import Metric

from pww.utilities.metrics import build_race_metrics


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Get Results script..")
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        for race in Race.objects.filter(
            chart__program__date__range=(
                yesterday, today)):
            chart = race.chart
            time = chart.time
            program = chart.program
            date = program.date
            venue = program.venue
            results_url = build_race_results_url(
                venue.code,
                date.year,
                date.month,
                date.day,
                time,
                race.number)
            print(results_url)
            page_data = get_node_elements(results_url, '//td')
            if len(page_data) > 85:
                parse_results_url(results_url, race, page_data)

        new_job = CronJob(
            type="Results"
        )
        new_job.set_fields_to_base()
        new_job.save()
