from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    balance = models.DecimalField(decimal_places=2, max_digits=10)
    rating = models.DecimalField(decimal_places=2, max_digits=10)
    emp_title = models.CharField(max_length=256)
    annual_income = models.DecimalField(decimal_places=2, max_digits=10)
    is_creditor = models.BooleanField(default=False)
