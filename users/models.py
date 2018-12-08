from collections import Counter
from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractUser
from django_cryptography.fields import encrypt

from finance.exceptions import TransferError


class DebitCards(Enum):
    visa = 'visa'
    master_card = 'mast'
    maestro = 'maes'

    @classmethod
    def get_choices(cls):
        return tuple((i.name, i.value) for i in cls)


class Balance(models.Model):
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CreditCard(models.Model):
    connected_balance = models.ForeignKey(Balance, related_name='cards', on_delete=models.CASCADE)
    card_type = encrypt(models.CharField(max_length=4, choices=DebitCards.get_choices()))
    number = encrypt(models.CharField(max_length=16))
    cvc_code = encrypt(models.CharField(max_length=3))
    expiration_date = encrypt(models.CharField(max_length=3))
    owner = encrypt(models.CharField(max_length=128))


class User(AbstractUser):
    balance = models.OneToOneField(Balance, related_name='owner', on_delete=models.CASCADE, null=True, blank=True)
    rating = models.DecimalField(decimal_places=2, max_digits=10, default=0, null=True, blank=True)
    emp_title = models.CharField(max_length=256, null=True, blank=True)
    annual_income = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    is_creditor = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    telephone = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField()
    passport_number = models.CharField(max_length=128, null=True, blank=True)

    OPTIONAL_FIELDS = (
        'rating',
        'emp_title',
        'annual_income',
        'telephone',
        'first_name',
        'last_name',
        'passport_number',
    )

    @property
    def complete(self):
        for field in self.OPTIONAL_FIELDS:
            value = getattr(self, field)
            if value != False and not bool(value):
                return False
        return True

    def withdraw(self, amount):
        if amount > self.balance.balance:
            raise TransferError("Insufficient funds")

        self.balance.balance -= amount
        self.balance.save()

    def replenish(self, amount):
        self.balance.balance += amount
        self.balance.save()

    def get_debts_stats(self):
        return Counter([debt.status for debt in self.debts.all()])

    def get_rating_stats(self):
        return [summary.rating for summary in self.summaries.order_by('date').all()]

    def get_finance_stats(self):
        return {
            "all_time": {
                "income": sum([credit.total_pay_amount for credit in self.credits.all()]),
                "total_debt": sum([debt.total_pay_amount for debt in self.debts.filter().all()]),
            },
            "active_last_month": {
                "income": sum([credit.current_size for credit in self.credits.all() if credit.active]),
                "total_debt": sum([debt.current_size for debt in self.debts.filter().all() if debt.active]),
            }

        }

    def get_all_stats(self):
        return {
            "debts": self.get_debts_stats(),
            "rating": self.get_rating_stats(),
            "finance": self.get_finance_stats(),
        }

    def to_json(self):
        return {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "balance": self.balance.balance,
            "rating": self.rating,
            "emp_title": self.emp_title,
            "annual_income": self.annual_income,
            "is_creditor": self.is_creditor,
            "is_locked": self.is_locked
        }
