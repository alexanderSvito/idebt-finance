import random

from abc import ABCMeta

from django.test import TestCase
from tests.helpers import create_user
from users.models import User


class AbstractTestCase(TestCase, metaclass=ABCMeta):
    CREDITOR_COUNT = 10
    BORROWER_COUNT = 10
    SEED = (11 >> 107) ^ (31 >> 17)

    def setUp(self):
        random.seed(self.SEED)
        self.system = self.create_system()
        self.creditors = [
            self.create_user(is_superuser=False, is_creditor=True)
            for _ in range(self.CREDITOR_COUNT)
        ]
        self.borrowers = [
            self.create_user(is_superuser=False, is_creditor=False)
            for _ in range(self.BORROWER_COUNT)
        ]

    def get_borrower(self):
        return random.choice(self.creditors)

    def get_creditor_with_balance(self, balance):
        creditor = random.choice(self.creditors)
        if creditor.balance.balance <= balance:
            creditor.replenish(balance * 1.1 - creditor.balance.balance)
        else:
            creditor.withdraw(creditor.balance.balance - balance)

        creditor.balance.save()

        return creditor

    def create_user(self, is_superuser=False, is_creditor=False):
        user, created = User.objects.get_or_create(**create_user())
        if is_superuser:
            user.is_superuser = True
            user.is_staff = True

        user.is_creditor = is_creditor

        user.save()

        return user

    def create_system(self):
        user, created = User.objects.get_or_create({
            "username": "system",
            "password": "system",
            "annual_income": 0,
        })

        return user

    def assertHasError(self, instance, field, msg):
        self.assertIn(field, instance.errors)
        self.assertIn(
            msg,
            instance.errors[field]
        )
