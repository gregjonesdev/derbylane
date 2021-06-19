import sys

from django.core.management.base import BaseCommand

from miner.utilities.scrape import single_url_test

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str)


    def handle(self, *args, **options):
        url = sys.argv[3]
        url = "https://m.trackinfo.com/index.jsp?next=resultsrace&raceid=GSL$20210617T16"
        # tds = get_node_elements(url, '//td')
        # if len(page_data) > 20:
        # raw_setting = get_raw_setting(page_data) # Race, 1
        chart = None
        single_url_test(url, chart)
