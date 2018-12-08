from django.db import models

from users.models import User


class TimestampMixin(models.Model):
    date = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True


class UserRatingSummary(TimestampMixin):
    user = models.ForeignKey(User, related_name='summaries', on_delete=models.CASCADE)
    rating = models.IntegerField()
    income = models.DecimalField(max_digits=10, decimal_places=2)
    debts_count = models.IntegerField()
    total_debt = models.DecimalField(max_digits=10, decimal_places=2)
