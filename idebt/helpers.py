import datetime

from django.utils import timezone
from django.conf import settings
from users.models import User


def get_days_from_to_date(date_from, date_to=timezone.now().date()):
    if isinstance(date_from, datetime.datetime):
        date_from = date_from.date()
    return (date_to - date_from).days


def get_admin():
    return User.objects.get(username=settings.SYSTEM_USERNAME)


