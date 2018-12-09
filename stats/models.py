from django.db import models

from users.models import User


class TimestampMixin(models.Model):
    date = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True


class UserRatingSummary(TimestampMixin):
    user = models.ForeignKey(User, related_name='summaries', on_delete=models.CASCADE)
    rating = models.IntegerField()
    income = models.DecimalField(max_digits=50, decimal_places=2)
    debts_count = models.IntegerField()
    total_debt = models.DecimalField(max_digits=50, decimal_places=2)

    def to_json(self):
        return {
            "date": self.date,
            "rating": self.rating,
            "income": self.income,
            "debts_count": self.debts_count,
            "total_debt": self.total_debt
        }


class CurrencySummary(TimestampMixin):
    base = models.CharField(max_length=3)
    currency = models.CharField(max_length=3)
    base_rate = models.DecimalField(max_digits=50, decimal_places=10)
    currency_rate = models.DecimalField(max_digits=50, decimal_places=10)
