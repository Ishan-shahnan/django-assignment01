from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User

from users.models import CustomUser


class Command(BaseCommand):
    help = 'Set up Role-Based Access Control groups and assign default roles'

    def handle(self, *args, **options):
        core_groups = ['Admin', 'Organizer', 'Participant']
        
        for group_name in core_groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created group: {group_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Group already exists: {group_name}')
                )
        

        admin_group = Group.objects.get(name='Admin')
        superusers = CustomUser.objects.filter(is_superuser=True)
        
        for user in superusers:
            if not user.groups.filter(name='Admin').exists():
                user.groups.add(admin_group)
                self.stdout.write(
                    self.style.SUCCESS(f'Assigned Admin role to superuser: {user.username}')
                )
        
        participant_group = Group.objects.get(name='Participant')
        users_without_groups = CustomUser.objects.filter(groups__isnull=True, is_superuser=False)
        
        for user in users_without_groups:
            user.groups.add(participant_group)
            self.stdout.write(
                self.style.SUCCESS(f'Assigned Participant role to user: {user.username}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('RBAC setup completed successfully!')
        )