"""
Create Django groups for Rentify users.
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create the required Django groups."""

    GROUPS = ("GUEST", "HOST", "BOTH")

    def handle(self, *args, **options):
        """Create groups if they do not already exist."""

        for group_name in self.GROUPS:
            group, created = Group.objects.get_or_create(name=group_name)

            if created:self.stdout.write(self.style.SUCCESS(f"Created group: {group_name}"))
            else:
                self.stdout.write(
                    f"Group already exists: {group_name}")

        self.stdout.write(
            self.style.SUCCESS("Django Groups setup completed successfully."))
