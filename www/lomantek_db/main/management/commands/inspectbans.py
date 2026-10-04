from django.core.management.base import BaseCommand
from main import models
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Check the ban time && disable the users of banned id's"

    def handle(self, *args, **options):
        for object in models.Id.objects.all():
            if object.is_banned == True:
                self.stdout.write(f"Info: User {object.user.username} has banned! Scanning them... ")
                if object.unban_time is not None and object.unban_time <= timezone.now().date() and not object.ban_permanent:
                    self.stdout.write(f"Info: User {object.user.username} ban time is ended! Unbanning them...")
                    object.is_banned = False
                    object.ban_time = None
                    object.ban_permanent = False
                    object.unban_time = None
                    object.save()
                    self.stdout.write(f"Info: User {object.user.username} has unbanned!")
                    continue

                if object.ban_permanent and object.ban_time is not None and object.ban_time + timedelta(days=365) <= timezone.now().date():
                    self.stderr.write(f"Warning: User {object.user.username} has banned permanent and year has passed! Deleting them...")
                    object.user.delete()
                    continue
            else:
                self.stdout.write(f"Info: User {object.user.username} is not banned! Clearing ban fields of them...")
                object.ban_time = None
                object.ban_permanent = False
                object.unban_time = None
                object.save()
                self.stdout.write(f"Info: Ban fields of user {object.user.username} has cleared!")
