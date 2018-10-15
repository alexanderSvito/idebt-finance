from django.db import models
from django.contrib.auth.models import AbstractUser


class Balance(models.Model):
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class User(AbstractUser):
    balance = models.OneToOneField(Balance, related_name='owner', on_delete=models.CASCADE)
    rating = models.DecimalField(decimal_places=2, max_digits=10, default=50)
    emp_title = models.CharField(max_length=256)
    annual_income = models.DecimalField(decimal_places=2, max_digits=10)
    is_creditor = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    telephone = models.CharField(max_length=32)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    passport_number = models.CharField(max_length=128)

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
