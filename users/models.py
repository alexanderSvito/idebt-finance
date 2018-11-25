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
    balance = models.OneToOneField(Balance, related_name='owner', on_delete=models.CASCADE, null=True)
    rating = models.DecimalField(decimal_places=2, max_digits=10, default=0, blank=True)
    emp_title = models.CharField(max_length=256, blank=True)
    annual_income = models.DecimalField(decimal_places=2, max_digits=10, blank=True)
    is_creditor = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    telephone = models.CharField(max_length=32, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField()
    passport_number = models.CharField(max_length=128, blank=True)

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
