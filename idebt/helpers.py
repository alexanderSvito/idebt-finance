from django.utils import timezone


def get_days_from_to_date(date_from, date_to=timezone.now()):
    return (date_to - date_from).days
