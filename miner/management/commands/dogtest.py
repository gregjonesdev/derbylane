from django.core.management.base import BaseCommand

from rawdat.models import Dog

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Magic number: 24")
        dog = Dog.objects.get(name="SUPER C DEMURE")
        parts = dog.participant_set.filter(
            race__distance=550,
            race__condition__name="F",
            final__isnull=False,
        )
        for part in parts:
            print(part.race.chart.program.date)
