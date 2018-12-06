import random

from finance.models import *
from django.core.management.base import BaseCommand

from finance.serializers import MatchSerializer
from tests.helpers import create_issue, create_offer, get_balance, create_user
from users.serializers import UserSerializer, PasswordSerializer


class Command(BaseCommand):
    help = 'Creates a system account'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--truncate', default=True, action='store_false')

    def handle(self, *args, **options):
        if options['truncate']:
            try:
                user = User.objects.get(username='system')
                user.delete()
                self.stdout.write("System cleared")
            except User.DoesNotExist:
                pass

        serializer = UserSerializer(data={
            "username": "system",
            "email": "admin@idebt.com",
            "passport_number": "AAAAAAAA-AAAAAAAA",
            "balance": 1000000,
            "password": settings.SYSTEM_PASSWORD
        })
        if serializer.is_valid():
            password = PasswordSerializer(data={
                "password": settings.SYSTEM_PASSWORD
            })
            if password.is_valid():
                user = serializer.save()
                password = password.save()
                user.password = password
                user.save()
                self.stdout.write("Success")
            else:
                self.stderr.write(str(serializer.errors))
        else:
            self.stderr.write(str(serializer.errors))
