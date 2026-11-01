from django.core.management.base import BaseCommand
from main import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Check the ban time && disable the users of banned id's"

    def handle(self, *args, **options):
        users_to_delete = []
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
                    self.stderr.write(f"Warning: User {object.user.username} has banned permanent and year has passed! Them has deleted after checking other users!")
                    users_to_delete.append(object.user.id)
                    continue
            else:
                if object.ban_time is None and object.ban_permanent is None and object.unban_time is None:
                    self.stdout.write(f"Info: User {object.user.username} is not banned and ban fields of them has empty!")
                    continue
                self.stdout.write(f"Info: User {object.user.username} is not banned! Clearing ban fields of them...")
                object.ban_time = None
                object.ban_permanent = False
                object.unban_time = None
                object.save()
                self.stdout.write(f"Info: Ban fields of user {object.user.username} has cleared!")

        self.stdout.write("Info: Users checking ended! Deleting users from delete list!")

        if users_to_delete == []:
            self.stdout.write("Info: Nothing to delete. Skiping this step")
        else:
            self.stderr.write(f"Warning: {len(users_to_delete)} users has been deleted!")

            User.objects.filter(id__in=users_to_delete).delete()

            self.stdout.write("Info: users from delete list has deleted successfully!")

        self.stdout.write("This action has completed successfully")
