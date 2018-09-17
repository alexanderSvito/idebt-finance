from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
	email = models.EmailField()
	rating = models.DecimalField()
    emp_title = models.StringField()
    annual_income = models.DecimalField(decimal_places=2)
    is_creditor = models.BooleanField(default=False)
