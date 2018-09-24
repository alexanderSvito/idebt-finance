import os
import random

from users.models import *
from finance.models import *
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


DATA_DIR = os.path.join(settings.BASE_DIR, 'idebt','data')
USERNAMES = open(os.path.join(DATA_DIR, 'usernames.txt')).readlines()
FIRST_NAMES_MALE = open(os.path.join(DATA_DIR, 'names_male.txt')).readlines()
FIRST_NAMES_FEMALE = open(os.path.join(DATA_DIR, 'names_female.txt')).readlines()
LAST_NAMES = open(os.path.join(DATA_DIR, 'last_names.txt')).readlines()
EMAIL_DOMAINS = open(os.path.join(DATA_DIR, 'email_domains.txt')).readlines()
JOB_TITLES = open(os.path.join(DATA_DIR, 'emp_titles.txt')).readlines()


def get_gender():
    return 'male' if random.randint(0, 1) else 'female'


def get_username():
    return random.choice(USERNAMES).strip()


def get_name(gender):
    if gender == 'male':
        first_name = random.choice(FIRST_NAMES_MALE).strip()
    else:
        first_name = random.choice(FIRST_NAMES_FEMALE).strip()
    last_name = random.choice(LAST_NAMES).strip()
    return first_name, last_name


def get_email(username):
    return username + "@" + random.choice(EMAIL_DOMAINS).strip()


def get_rating():
    return round(random.random() * 100, 2)


def get_balance(rating):
    min, max = 0, 5000
    mode = int((max - min) * (rating / 100))
    return round(random.triangular(min, max, mode), 2)


def get_employment_title(rating):
    if rating < 0.2:
        return "Unemployed"
    else:
        return random.choice(JOB_TITLES).strip()


def get_annual_income(rating):
    min, max = 0, 120000
    mode = int((max - min) * (rating / 100))
    return round(random.triangular(min, max, mode), 2)


def get_is_creditor():
    return random.random() < 0.65


def create_user():
    username = get_username()
    gender = get_gender()
    first_name, last_name = get_name(gender)
    rating = get_rating()
    return {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'email': get_email(username),
        'balance': get_balance(rating),
        'rating': rating,
        'emp_title': get_employment_title(rating),
        'annual_income': get_annual_income(rating),
        'is_creditor': get_is_creditor(),
    }


class Command(BaseCommand):
    help = 'Populates the database with seed data'

    def handle(self, *args, **options):
        for _ in range(10):
            self.stdout.write(str(create_user()))
