from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from datetime import datetime
from rawdat.models import Bet_Recommendation
from rawdat.models import Venue, Grade

classifiers = {
    'j48': [
    ['WD', 'A', 548, 0.4, "2020-01-01", 24, 1, 3, "P"],
    ['WD', 'B', 548, 0.4, "2020-01-01", 24, 1, 4, "P"],
    ['WD', 'B', 548, 0.5, "2020-01-01", 24, 1, 1, "PS"],
    ['WD', 'C', 548, 0.4, "2020-01-01", 24, 1, 0, "P"],
    ['TS', 'A', 550, 0.5, "2019-06-01", 18, 0.7, 0, "WP"],
    ['TS', 'A', 550, 0.5, "2019-06-01", 18, 1, 1, "PS"],
    ['TS', 'B', 550, 0.5, "2019-06-01", 18, 0.8, 1, "WPS"],
    ['TS', 'C', 550, 0.4, "2020-01-01", 24, 1, 0, "P"],
    ],
}


class Command(BaseCommand):

    def build_recommendation(
        self,
        classifier,
        venue_code,
        grade_name,
        distance,
        c_factor,
        start_date,
        months,
        cutoff,
        prediction,
        rec_bet):
        venue = Venue.objects.get(code=venue_code)
        grade = Grade.objects.get(name=grade_name)
        try:
            recommendation = Bet_Recommendation.objects.get(
                venue=venue,
                grade=grade,
                classifier=classifier,
                c_factor=c_factor,
                cutoff=cutoff,
                distance=distance,
                prediction=prediction)
        except ObjectDoesNotExist:
            new_recommendation = Bet_Recommendation(
                venue=venue,
                grade=grade,
                classifier=classifier,
                c_factor=c_factor,
                cutoff=cutoff,
                start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                months=months,
                distance=distance,
                prediction=prediction,
                bet=rec_bet)
            new_recommendation.set_fields_to_base()
            new_recommendation.save()

    def handle(self, *args, **options):
        for classifier in classifiers:
            for recommendation in classifiers[classifier]:
                self.build_recommendation(
                    classifier,
                    recommendation[0],
                    recommendation[1],
                    recommendation[2],
                    recommendation[3],
                    recommendation[4],
                    recommendation[5],
                    recommendation[6],
                    recommendation[7],
                    recommendation[8])
