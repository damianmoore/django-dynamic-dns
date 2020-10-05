import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = 'Ensure admin user is set up'

    def handle(self, **options):
        if User.objects.filter(is_superuser=True).count():
            print('Admin user already exists')
        else:
            user_data = {
                'username': os.environ.get('ADMIN_USER', 'admin'),
                'password': os.environ.get('ADMIN_PASSWORD', 'password'),
            }

            User.objects.create_superuser(**user_data)
            print('Admin user created')
