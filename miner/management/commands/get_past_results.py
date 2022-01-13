import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.core.management.base import BaseCommand

from miner.utilities.common import get_node_elements
from miner.utilities.scrape import single_url_test
from miner.utilities.urls import build_race_results_url
from rawdat.models import Race, CronJob

from pww.utilities.metrics import build_race_metrics


class Command(BaseCommand):

    def handle(self, *args, **options):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=9)
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
            tds = get_node_elements(results_url, '//td')
            single_url_test(results_url, tds, chart)

        new_job = CronJob(
            type="Results"
        )
        new_job.set_fields_to_base()
        new_job.save()
