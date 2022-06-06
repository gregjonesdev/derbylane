from django.core.management.base import BaseCommand

from rawdat.models import Dog

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Magic number: 24")
        target_date="2022-06-01"
        race_count = 5
        dog = Dog.objects.get(name="SUPER C DEMURE")
        parts = dog.participant_set.filter(
            race__chart__program__date__lt=target_date,
            race__distance=550,
            race__condition__name="F",
            final__isnull=False,
            ).order_by(
                '-race__chart__program__date')[:race_count]
        for part in parts:
            print(part.race.chart.program.date)
