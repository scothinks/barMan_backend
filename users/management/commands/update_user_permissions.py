from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

class Command(BaseCommand):
    help = 'Update user permissions'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to update')
        parser.add_argument('--inventory', type=str, choices=['true', 'false'], help='Can update inventory')
        parser.add_argument('--sales', type=str, choices=['true', 'false'], help='Can report sales')
        parser.add_argument('--customers', type=str, choices=['true', 'false'], help='Can create customers')
        parser.add_argument('--create-tabs', type=str, choices=['true', 'false'], help='Can create tabs')
        parser.add_argument('--update-tabs', type=str, choices=['true', 'false'], help='Can update tabs')
        parser.add_argument('--manage-users', type=str, choices=['true', 'false'], help='Can manage users')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            return

        permissions = ['inventory', 'sales', 'customers', 'create_tabs', 'update_tabs', 'manage_users']
        for perm in permissions:
            if options[perm] is not None:
                setattr(user, f'can_{perm}', options[perm].lower() == 'true')

        user.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated permissions for user "{username}"'))