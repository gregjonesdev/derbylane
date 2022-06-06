from django.core.management.base import BaseCommand

from rawdat.models import Dog

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Magic number: 28")
        dog = Dog.objects.get(name="SUPER C DEMURE")
        print(dog.participant_set.all().count())
