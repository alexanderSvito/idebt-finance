from datetime import datetime


def get_days_from_to_date(date_from, date_to=datetime.now()):
    return (date_to - date_from).days
