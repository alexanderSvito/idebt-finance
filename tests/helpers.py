import os
import random
import string

from decimal import Decimal as D

from django.conf import settings


DATA_DIR = os.path.join(settings.BASE_DIR, 'idebt', 'data')
USERNAMES = open(os.path.join(DATA_DIR, 'usernames.txt')).readlines()
FIRST_NAMES_MALE = open(os.path.join(DATA_DIR, 'names_male.txt')).readlines()
FIRST_NAMES_FEMALE = open(os.path.join(DATA_DIR, 'names_female.txt')).readlines()
LAST_NAMES = open(os.path.join(DATA_DIR, 'last_names.txt')).readlines()
EMAIL_DOMAINS = open(os.path.join(DATA_DIR, 'email_domains.txt')).readlines()
JOB_TITLES = open(os.path.join(DATA_DIR, 'emp_titles.txt')).readlines()


def get_gender():
    return 'male' if random.randint(0, 1) else 'female'


def get_username():
    username = random.choice(USERNAMES)
    USERNAMES.remove(username)
    return username.strip()


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


def get_digit_string(n):
    return "".join(random.choice(string.digits) for i in range(n))


def get_telephone():
    country_code = get_digit_string(random.randint(1, 3))
    code = get_digit_string(random.randint(2, 3))
    phone = "{}-{}-{}".format(
        get_digit_string(3),
        get_digit_string(2),
        get_digit_string(2)
    )
    return "+{}({}){}".format(country_code, code, phone)


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


def get_passport_number():
    possible_letters = string.ascii_uppercase + string.digits
    return "{}-{}".format(
        "".join(random.sample(possible_letters, 10)),
        "".join(random.sample(possible_letters, 10))
    )


def get_password():
    return "".join(random.sample(string.printable * 3, random.randint(8, 15)))


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
        'rating': rating,
        'password': get_password(),
        'balance': get_balance(rating),
        'emp_title': get_employment_title(rating),
        'annual_income': get_annual_income(rating),
        'is_creditor': get_is_creditor(),
        'telephone': get_telephone(),
        'passport_number': get_passport_number()
    }


def create_offer(user):
    credit_fund = round(user.balance.balance * D(random.triangular(0, 1, 0.2)))
    max_loan_size = round(random.triangular(credit_fund / 10, credit_fund, credit_fund / 5))
    min_loan_size = round(random.triangular(credit_fund / 20, credit_fund / 10, credit_fund / 15))
    percentage = random.random() * 10
    is_with_capitalization = random.random() < 0.25
    return_period = random.randint(7, 62)
    grace_period = int(return_period * random.random() * 0.5)
    return {
        'credit_fund': credit_fund,
        'min_loan_size': min_loan_size,
        'max_loan_size': max_loan_size,
        'credit_percentage': percentage,
        'is_with_capitalization': is_with_capitalization,
        'grace_period': grace_period,
        'return_period': return_period,
    }


def create_issue(user):
    amount = round(user.balance.balance * D(random.triangular(0.5, 3.0, 1.25)))
    max_overpay = amount * random.random() * 5
    min_credit_period = random.randint(3, 31)
    return {
        'amount': amount,
        'max_overpay': max_overpay,
        'min_credit_period': min_credit_period
    }

