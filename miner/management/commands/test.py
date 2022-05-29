import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.core.management.base import BaseCommand

from miner.utilities.common import get_node_elements
from miner.utilities.new_scrape import process_url, has_results
from miner.utilities.urls import build_race_results_url
from rawdat.models import Race, Participant

from pww.utilities.metrics import build_race_metrics


class Command(BaseCommand):

    def handle(self, *args, **options):
        url = "http://m.trackinfo.com/index.jsp?next=resultsrace&raceid=GTS$20220204E08"

        race = Race.objects.get(
            chart__program__venue__code="TS",
            chart__program__date="2022-02-04",
            chart__time="E",
            number=8)


#
        print("{} {} {} Race {}".format(
            race.chart.program.venue.code,
            race.chart.program.date,
            race.chart.time,
            race.number
        ))

        for superfecta in race.sizzle_superfecta_set.all():
            print("{} / {} / {} / {}\t${}".format(
                superfecta.win_post,
                superfecta.place_post,
                superfecta.show_post,
                superfecta.fourth_post,
                superfecta.payout
            ))

        for trifecta in race.sizzle_trifecta_set.all():
            print("{} / {} / {}\t${}".format(
                trifecta.win_post,
                trifecta.place_post,
                trifecta.show_post,
                trifecta.payout
            ))
        #
        for exacta in race.sizzle_exacta_set.all():
            print("{} / {}\t${}".format(
                exacta.win_post,
                exacta.place_post,
                exacta.payout
            ))

        for quinella in race.sizzle_quinella_set.all():
            print("{} / {}\t${}".format(
                quinella.left_post,
                quinella.right_post,
                quinella.payout
            ))

        for participant in race.participant_set.all():
            print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
            participant.dog.name,
            participant.post,
            participant.off,
            participant.eighth,
            participant.straight,
            participant.final,
            participant.actual_running_time,
            participant.lengths_behind
            ))
