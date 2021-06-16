import sys

from django.core.management.base import BaseCommand

from miner.utilities.scrape import scan_url

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str)


    def handle(self, *args, **options):
        url = sys.argv[3]
        url = "https://m.trackinfo.com/index.jsp?next=resultsrace&raceid=GIG$20210616E01"
        scan_url(url)
