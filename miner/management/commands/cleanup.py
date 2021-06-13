from django.core.management.base import BaseCommand

from rawdat.models import Participant, Dog
from miner.utilities.urls import build_race_results_url

from pww.models import Metric


class Command(BaseCommand):

    def handle(self, *args, **options):
        wrong = Dog.objects.get(name="CET EASI ELI")
        right = Dog.objects.get(name="CET EASY ELI")
        for participant in wrong.participant_set.all():
            participant.dog_id = right.uuid
            participant.save()
