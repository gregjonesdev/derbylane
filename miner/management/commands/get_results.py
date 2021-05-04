import datetime

from django.core.management.base import BaseCommand

from rawdat.models import Program

from miner.utilities.scrape import (
    build_results_url,
    check_for_results,
    )

from miner.utilities.common import get_node_elements


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Get Results script..")
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        # for program in Program.objects.filter(
        #     date__range=(yesterday, today),
        #     venue__in=active_venues):
        #     venue = program.venue
        #     for chart in program.chart_set.all():
        #         print(chart.time)
        for program in Program.objects.all():
            date = program.date
            venue = program.venue
            for chart in program.chart_set.all():
                time = chart.time
                for race in chart.race_set.all():
                    target_url = build_results_url(
                        venue.code,
                        date.year,
                        date.month,
                        date.day,
                        time,
                        race.number)
                    print(target_url)
                    page_data = get_node_elements(target_url, '//td')
                    div_tds = get_node_elements(target_url, '//td//div')
                    check_for_results(race, page_data, div_tds)
