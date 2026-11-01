from django.core.management.base import BaseCommand
from main import models

class Command(BaseCommand):
    help = "Check the users related models!"

    def handle(self, *args, **kwargs):
        for obj in models.Id.objects.all():
            obj.check_models()
            self.stdout.write(f"{str(obj)} has checked")

        self.stdout.write("This action has completed successfully!")
