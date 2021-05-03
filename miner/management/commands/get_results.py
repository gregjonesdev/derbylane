from django.core.management.base import BaseCommand

from rawdat.models import (
    Program,
    )

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Get Results script..")
        
