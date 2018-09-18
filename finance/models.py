from enum import Enum

from django.db import models
from idebt.helpers import get_days_from_to_date


class DeptStatus(Enum):
    CLOSED = 'closed'
    FAILED = 'failed'
    PENDING = 'pending'
    FROZEN = 'frozen'


class AbstractLoan(models.Model):
    credit_percentage = models.DecimalField(decimal_places=2)
    is_with_capitalization = models.BooleanField(default=False)

    grace_period = models.IntegerField(default=0)
    return_period = models.IntegerField()

    class Meta:
        abstract = True


class Offer(AbstractLoan):
    credit_fund = models.DecimalField(decimal_places=2)
    min_loan_size = models.DecimalField(decimal_places=2)
    max_loan_size = models.DecimalField(decimal_places=2)

    def overpay_for(self, loan_size):
        percent_days = self.return_period - self.grace_period
        if self.is_with_capitalization:
            return loan_size * (1 + self.credit_percentage) ** percent_days
        else:
            return loan_size * (1 + percent_days * self.credit_percentage)

    def to_json(self):
        return {
            'credit_fund': self.credit_fund,
            'min_loan_size': self.min_loan_size,
            'max_loan_size': self.max_loan_size,
            'percentage': self.credit_percentage,
            'is_with_capitalization': self.is_with_capitalization,
            'grace_period': self.grace_period,
            'return_period': self.return_period,
        }


class Issue(models.Model):
    amount = models.DecimalField(decimal_places=2)
    max_overpay = models.DecimalField(decimal_places=2)
    max_credit_period = models.IntegerField()

    def to_json(self):
        return {
            'desired_size': self.amount,
            'max_overpay': self.max_overpay,
            'max_credit_period': self.max_credit_period
        }


class Debt(AbstractLoan):
    created_at = models.DateTimeField(auto_add=True)
    loan_size = models.DecimalField(decimal_places=2)
    credit = models.ForeignKey(Offer, related_name="loans", on_delete=models.SET_NULL)
    is_closed = models.BooleanField(default=False)
    is_frozen = models.BooleanField(default=False)

    @property
    def status(self):
        days_passed = get_days_from_to_date(self.created_at)
        if self.is_closed:
            return DeptStatus.CLOSED
        elif self.is_frozen:
            return DeptStatus.FROZEN
        elif days_passed > self.return_period:
            return DeptStatus.FAILED
        else:
            return DeptStatus.PENDING

    @property
    def current_size(self):
        days_passed = get_days_from_to_date(self.created_at)
        return self._count_size_for_days(days_passed)

    @property
    def size_in_week(self):
        days_passed = get_days_from_to_date(self.created_at)
        return self._count_size_for_days(days_passed + 7)

    @property
    def size_in_month(self):
        days_passed = get_days_from_to_date(self.created_at)
        return self._count_size_for_days(days_passed + 30)


    def to_json(self):
        return {
            'status': self.status,
            'initial_size': self.loan_size,
            'current_size': self.current_size,
            'size_in_week': self.size_in_week,
            'size_in_month': self.size_in_month,
            'percentage': self.credit_percentage,
            'created_at': self.created_at,
            'is_with_capitalization': self.is_with_capitalization
        }
