import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.core.management.base import BaseCommand

from miner.utilities.common import get_node_elements
from miner.utilities.scrape import single_url_test
from miner.utilities.urls import build_race_results_url
from rawdat.models import Race, CronJob, Chart

from pww.utilities.metrics import build_race_metrics

chart_times = {
    "TS": ['A', 'E', 'S', 'T'],
    "WD": ['A', 'E', 'S'],
    "SL": ['A', 'E', 'S', 'T']
}

class Command(BaseCommand):

    def handle(self, *args, **options):
        today = datetime.date.today()
        start = today - datetime.timedelta(days=28)
        for venue_code in ["TS", "WD", "SL"]:
            for chart_time in chart_times[venue_code]:
                results_url = build_race_results_url(
                    venue_code,
                    date.year,
                    date.month,
                    date.day,
                    time,
                    race.number)
            # tds = get_node_elements(results_url, '//td')
            # single_url_test(results_url, tds, chart)
