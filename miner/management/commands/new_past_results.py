import sys

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from concurrent.futures import ThreadPoolExecutor

from miner.utilities.urls import build_race_results_url
from miner.utilities.common import get_node_elements
from miner.utilities.constants import chart_times
from miner.utilities.comments import no_elements
from miner.utilities.models import get_program, get_chart, get_race
from miner.utilities.new_scrape import save_race_results, save_race_settings

from rawdat.models import ScannedUrl, Venue

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int)

    def get_scan(self, url):
        try:
            scan = ScannedUrl.objects.get(address=url)
        except ObjectDoesNotExist:
            new_scan = ScannedUrl(address=url)
            new_scan.set_fields_to_base()
            new_scan.save()
            scan = new_scan
        return scan

    def update_scan(self, scan, comment):
        scan.comment = comment
        if comment in ["No <td> Elements"]:
            scan.completed = True
        scan.save()

    def scan_day(self, venue_code, month, year, day):
        venue = Venue.objects.get(code=venue_code)
        program = get_program(
            venue,
            "{}-{}-{}".format(
                year,
                str(month).zfill(2),
                str(day).zfill(2)
            )
        )
        for time in chart_times:
            chart = get_chart(program, time)
            number = 1
            while number <= 30:
                comment = None
                url = build_race_results_url(
                    venue_code,
                    year,
                    str(month).zfill(2),
                    str(day).zfill(2),
                    time,
                    str(number).zfill(2))
                scan = self.get_scan(url)
                if not scan.completed:
                    tds = get_node_elements(url, "//td")
                    trs = get_node_elements(url, "//tr")
                    if len(tds) > 15:
                        print(url)
                        race = get_race(chart, number)
                        if len(tds) > 33:
                            save_race_settings(race, tds)
                            comment = save_race_results(race, tds, trs)

                    else:
                        comment = no_elements







                    self.update_scan(scan, comment)
                number += 1

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
        #         build_race_from_url(url)


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
        # with ThreadPoolExecutor() as executor:
        #     executor.map(self.get_venue_results, venue_codes)

        self.get_venue_results('TS')



 #this is Similar to map(func, *iterables)
