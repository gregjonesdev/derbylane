from django.core.management.base import BaseCommand

from rawdat.models import Dog

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Magic number: 24")
        dog = Dog.objects.get(name="SUPER C DEMURE")
        print(dog.participant_set.filter(
            race__condition__name="F",
            final__isnull=False,
        ))
