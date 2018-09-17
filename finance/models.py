from django.db import models
from datetime import datetime


class CreditPlan(models.Model):
    credit_fund = models.DecimalField(decimal_places=2)
    min_loan_size = models.DecimalField(decimal_places=2)
    max_loan_size = models.DecimalField(decimal_places=2)

    credit_percentage = models.DecimalField(decimal_places=2)
    is_with_capitalization = models.BooleanField(default=False)

    grace_period = models.IntegerField(default=0)
    return_period = models.IntegerField()


class CreditIssue(models.Model):
    amount = models.DecimalField(decimal_places=2)
    max_overpay = models.DecimalField(decimal_places=2)
    credit_period = models.IntegerField()


class Debt(models.Model):
    created_at = models.DateTimeField(auto_add=True)
    loan_size = models.DecimalField(decimal_places=2)
    credit = models.ForeignKey(CreditPlan, related_name="loans", on_delete=models.SET_NULL)
    is_closed = models.BooleanField(default=False)

    def count_current_size(self, days_passed):
        if self.credit.is_with_capitalization:
            return None # TODO: Formula
        else:
            percent_days = days_passed - self.credit.grace_period
            return self.loan_size * (1 + percent_days * self.credit.credit_percentage)

    def current_status(self):
        today = datetime.now()
        days_passed = (today - self.created_at).days

        payload = {
            "return_period": self.credit.return_period,
            "credit_percentage": self.credit.credit_percentage,
        }

        if self.is_closed:
            payload['status'] = 'closed'
        elif days_passed > return_period:
            payload['status'] = 'failed'
            payload['loan_size'] =
        else:
            payload['status'] = 'pending'

            payload['days_left'] = return_period - days_passed
            payload['days_passed'] = days_passed

        return payload
