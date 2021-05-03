import json

from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Starting Bootstrap script..")
        data = open('./static/json/data.json').read()
        jsonData = json.loads(data)
        venues = jsonData["venues"]
        print(len(venues))
