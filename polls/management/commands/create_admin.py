"""
Django management command to create an admin user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create an admin user with authentication token'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the admin user (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Email for the admin user (default: admin@example.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for the admin user (default: admin123)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists!')
            )
            user = User.objects.get(username=username)
        else:
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user "{username}"')
            )

        # Create or get authentication token
        token, created = Token.objects.get_or_create(user=user)
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created authentication token for "{username}"')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Authentication token already exists for "{username}"')
            )

        # Display login information
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('ADMIN LOGIN INFORMATION'))
        self.stdout.write('='*50)
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Authentication Token: {token.key}')
        self.stdout.write('='*50)
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Log into Django admin at: /admin/')
        self.stdout.write('2. Use the API with the token for authenticated requests')
        self.stdout.write('3. Access user-specific endpoints like /api/user/profile/')
        self.stdout.write('='*50)
