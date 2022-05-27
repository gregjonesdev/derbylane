import sys
from concurrent.futures import ThreadPoolExecutor
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.core.management.base import BaseCommand

from rawdat.models import Venue, Race, Exotic_Bet_Type, Winning_Trifecta

from miner.utilities.scrape import scan_history_charts, single_url_test
from miner.utilities.urls import build_race_results_url
from miner.utilities.common import get_node_elements

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)

    def scan_month(self, venue, month, year):
        for race in Race.objects.filter(
            chart__program__venue=venue,
            chart__program__date__year=year,
            chart__program__date__month=month
        ):
            url = build_race_results_url(
                venue.code,
                year,
                month,
                race.chart.program.date.day,
                race.chart.time,
                race.number)
            self.process_url(url, race)

    def process_url(self, url, race):
        tds = get_node_elements(url, '//td')
        if len(tds) > 85:
            for td in tds:
                if len(td) > 0:
                    for child in td:
                        if child.text and "$2.00" in child.text:
                            split_text = child.text.split()
                            for entry in split_text:
                                if "/" in entry:
                                    posts_index =  split_text.index(entry)
                                    posts = entry
                            payout = split_text[-1]

                            type = split_text[1:posts_index]
                            if len(type) > 1:
                                new_type = ""
                                for each in type:
                                    new_type += "{} ".format(each)
                                type = new_type.strip()
                            else:
                                type = type[0]
                            # print(type)
                            if type.lower() == "trifecta":
                                post_list = posts.split("/")
                                for post in post_list:
                                    try:
                                        int(post)
                                    except:
                                        print(post_list)
                                        print(url)
                            # print(payout)

                            #     try:
                            #         winning_trifecta = Winning_Trifecta.objects.get(
                            #             race=race,
                            #
                            #         )

                            try:
                                exotic_bet_type = Exotic_Bet_Type.objects.get(
                                    name=type
                                )
                            except ObjectDoesNotExist:
                                exotic_bet_type = Exotic_Bet_Type(
                                    name=type
                                )
                                exotic_bet_type.set_fields_to_base()
                                exotic_bet_type.save()

        #         print("{}: {}".format(tds.index(td), td.text))
        #         if td.text and td.text.lower() == "exotics":
        #             exotics_cell_index = tds.index(td)
        # try:
        #     print(exotics_cell_index)
        # except UnboundLocalError:
        #     print("UH OH:")
        #     print(url)
        #     if len(tds) > 85:
        #         for td in tds:
        #             print("{}: {}".format(tds.index(td), td.text))
        #     raise SystemExit(0)

    def get_venue_results(self, venue_code):
        venue = Venue.objects.get(code=venue_code)
        year = sys.argv[3]
        month = 1
        while month <= 12:
            self.scan_month(venue, month, year)
            month += 1


    def handle(self, *args, **options):

        venue_codes = ['TS', 'WD', 'SL']

        self.get_venue_results('TS')

        # with ThreadPoolExecutor() as executor:
        #     executor.map(self.get_venue_results, venue_codes)





def download_images(url):
    img_name = img_url.split('/')[3]
    img_bytes = requests.get(img_url).content
    with open(img_name, 'wb') as img_file:
         img_file.write(img_bytes)
         print(f"{img_name} was downloaded")


 #this is Similar to map(func, *iterables)
