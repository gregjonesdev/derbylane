from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from rawdat.models import Bet_Recommendation
from rawdat.models import Venue, Grade

classifiers = {
    'smo': [
    ['WD', 'B', 548, 4, "P"],
    ['WD', 'C', 548, 2, "W"],
    ['TS', 'B', 550, 2, "P"],
    ['TS', 'C', 550, 1, "S"],
    ['SL', 'C', 583, 4, "WP"],
    ],
    'j48': [
    ['WD', 'B', 548, 1, "P"],
    ['WD', 'C', 548, 2, "W"],
    ['TS', 'B', 550, 2, "P"],
    ['TS', 'C', 550, 1, "S"],
    ['SL', 'C', 583, 4, "WP"],
    ],
}
]

class Command(BaseCommand):

    def build_recommendation(
        self,
        classifier,
        venue_code,
        grade_name,
        distance,
        prediction,
        rec_bet):
        venue = Venue.objects.get(code=venue_code)
        grade = Grade.objects.get(name=grade_name)
        try:
            recommendation = Bet_Recommendation.objects.get(
                venue=venue,
                grade=grade,
                classifier=classifier,
                distance=distance,
                prediction=prediction)
        except ObjectDoesNotExist:
            new_recommendation = Bet_Recommendation(
                venue=venue,
                grade=grade,
                distance=distance,
                prediction=prediction)
            new_recommendation.set_fields_to_base()
            new_recommendation.save()
            recommendation = new_recommendation
        recommendation.bet = rec_bet
        recommendation.save()

    def handle(self, *args, **options):
        for classifier in classifiers:
            for recommendation in classifiers[classifier]:
                self.build_recommendation(
                    classifier,
                    recommendation[0],
                    recommendation[1],
                    recommendation[2],
                    recommendation[3],
                    recommendation[4])
