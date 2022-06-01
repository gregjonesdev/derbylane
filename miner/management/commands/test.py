import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.core.management.base import BaseCommand

from miner.utilities.common import get_node_elements
from miner.utilities.scrape_results import process_url, has_results
from miner.utilities.urls import build_race_results_url
from rawdat.models import Race, Participant
from pww.utilities.metrics import get_prior_participations
from pww.utilities.metrics import build_race_metrics


class Command(BaseCommand):

    def handle(self, *args, **options):
        url = "http://m.trackinfo.com/index.jsp?next=resultsrace&raceid=GWD$20220529A01"

        race = Race.objects.get(
            chart__program__venue__code="WD",
            chart__program__date="2022-05-29",
            chart__time="A",
            number=1)


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
            for bet in participant.straight_bet_set.all():
                print("{}\t{}\t{}".format(
                    participant.dog.name,
                    bet.type.name,
                    bet.payout
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

            # priors = get_prior_participations(
            #     participant.dog,
            #     race.chart.program.date,
            #     race.distance,
            #     7)
