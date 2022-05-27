import sys
from concurrent.futures import ThreadPoolExecutor
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from miner.utilities.models import create_trifecta
from rawdat.models import ScannedUrl

from miner.utilities.urls import build_race_results_url
from miner.utilities.common import two_digitizer
from miner.utilities.constants import chart_times

from miner.utilities.new_scrape import process_url

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)

    def get_scan(url):
        try:
            return ScannedUrl.objects.get(
                address = url
            )
        except ObjectDoesNotExist:
            new_scan = ScannedUrl.objects.get(
                address = url
            )
            new_scan.set_fields_to_base()
            new_scan.save()
            return new_scan

    def scan_day(self, venue_code, month, year, day):
        for chart_time in chart_times:
            number = 0
            while number < 30:
                url = build_race_results_url(
                    venue_code,
                    year,
                    two_digitizer(month),
                    two_digitizer(day),
                    chart_time,
                    two_digitizer(number))
                scan = self.get_scan(url)

                # scan if not completed 




    def scan_month(self, venue_code, month, year):
        day = 1
        while day <= 31:
            self.scan_day(venue_code, month, year, day)
            day += 1
        # for race in month_races:
        #     url = build_race_results_url(
        #         race.chart.program.venue.code,
        #         year,
        #         two_digitizer(month),
        #         two_digitizer(race.chart.program.date.day),
        #         race.chart.time,
        #         two_digitizer(race.number))
        #     tds = get_node_elements(url, '//td')
        #     if len(tds) > 85:
        #
        #         process_url(url)


            # for td in tds:
            #     if len(td) > 0:
            #         for child in td:
            #             if child.text and "$2.00" in child.text:
            #                 split_text = child.text.split()
            #                 for entry in split_text:
            #                     if "/" in entry:
            #                         posts_index =  split_text.index(entry)
            #                         posts = entry
            #                 payout = split_text[-1]
            #                 float_payout = float(payout.replace(
            #                     "$", "").replace(
            #                     ",", ""))
            #                 type = split_text[1:posts_index]
            #                 if len(type) > 1:
            #                     new_type = ""
            #                     for each in type:
            #                         new_type += "{} ".format(each)
            #                     type = new_type.strip()
            #                 else:
            #                     type = type[0]
            #                 # print(type)
            #                 if type.lower() == "trifecta":
            #                     post_list = posts.split("/")
            #                     for post in post_list:
            #                         try:
            #                             int(post)
            #                         except:
            #                             # find posts in table
            #                             print(post_list)
            #                             print(url)
            #                 # print(payout)
            #
            #                     create_trifecta(race, posts, None, float_payout)

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
        year = sys.argv[3]
        month = 1
        while month <= 12:
            self.scan_month(venue_code, month, year)
            month += 1


    def handle(self, *args, **options):
        venue_codes = ['TS', 'WD', 'SL']
        with ThreadPoolExecutor() as executor:
            executor.map(self.get_venue_results, venue_codes)





def download_images(url):
    img_name = img_url.split('/')[3]
    img_bytes = requests.get(img_url).content
    with open(img_name, 'wb') as img_file:
         img_file.write(img_bytes)
         print(f"{img_name} was downloaded")


 #this is Similar to map(func, *iterables)
