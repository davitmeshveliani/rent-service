"""
Create Django groups and migrate existing user roles to groups.
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    """Create user groups and assign users based on their current role."""

    GROUPS = ("GUEST", "HOST", "BOTH")

    def handle(self, *args, **options):
        """Create groups and migrate existing user roles."""

        groups = {}
        for group_name in self.GROUPS:
            group, created = Group.objects.get_or_create(
                name=group_name)
            groups[group_name] = group

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created group: {group_name}"))
            else:
                self.stdout.write(f"Group already exists: {group_name}")
        users_updated = 0
        for user in User.objects.all():
            role = user.role

            if role not in groups:
                self.stdout.write(
                    self.style.WARNING(
                        f"Unknown role for {user.email}: {role}"))
                continue
            user.groups.set([groups[role]])
            users_updated += 1
        self.stdout.write(
            self.style.SUCCESS(f"Users assigned to groups: {users_updated}"))
        self.stdout.write(
            self.style.SUCCESS("Django Groups setup completed successfully."))