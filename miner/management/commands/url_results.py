import sys

from django.core.management.base import BaseCommand

from miner.utilities.scrape import single_url_test
from miner.utilities.common import get_node_elements

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str)


    def handle(self, *args, **options):
        url = sys.argv[3]
        url = "https://m.trackinfo.com/index.jsp?next=resultsrace&raceid=GSL$20210617T16"
        url = "http://m.trackinfo.com/index.jsp?next=resultsrace&raceid=GTS$20180103E01"
        chart = None
        tds = get_node_elements(url, '//td')
        single_url_test(url, tds, chart)
