from enum import Enum

from django.db import models
from idebt.helpers import get_days_from_to_date
from users.models import User


class DeptStatus(Enum):
    CLOSED = 'closed'
    FAILED = 'failed'
    PENDING = 'pending'
    FROZEN = 'frozen'


class AbstractLoan(models.Model):
    credit_percentage = models.DecimalField(decimal_places=2, max_digits=10)
    is_with_capitalization = models.BooleanField(default=False)

    grace_period = models.IntegerField(default=0)
    return_period = models.IntegerField()

    class Meta:
        abstract = True


class Offer(AbstractLoan):
    creditor = models.ForeignKey(User, related_name='offers', on_delete=models.CASCADE)
    credit_fund = models.DecimalField(decimal_places=2, max_digits=10)
    min_loan_size = models.DecimalField(decimal_places=2, max_digits=10)
    max_loan_size = models.DecimalField(decimal_places=2, max_digits=10)

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
    borrower = models.ForeignKey(User, related_name='issues', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    max_overpay = models.DecimalField(decimal_places=2, max_digits=10)
    max_credit_period = models.IntegerField()

    def to_json(self):
        return {
            'desired_size': self.amount,
            'max_overpay': self.max_overpay,
            'max_credit_period': self.max_credit_period
        }


class Debt(AbstractLoan):
    creditor = models.ForeignKey(User, related_name='credits', on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, related_name='debts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    loan_size = models.DecimalField(decimal_places=2, max_digits=10)
    credit = models.ForeignKey(Offer, related_name="loans", on_delete=models.CASCADE)
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

    @classmethod
    def create_from(cls, offer_id, issue_id):
        offer = Offer.objects.find(pk=offer_id)
        issue = Issue.objects.find(pk=issue_id)
        return cls.objects.create(
            loan_size=issue.amount,
            credit=offer,
            credit_percentage=offer.credit_percentage,
            is_with_capitalization=offer.is_with_capitalization,
            grace_period=offer.grace_period,
            return_period=offer.return_period
        )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        transaction = self.loan_size
        self.creditor.balance -= transaction
        self.borrower.balance += transaction
        self.creditor.save()
        self.borrower.save()
        super(Debt, self).save()

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


class Match(models.Model):
    OFFER = 'OFF'
    ISSUE = 'ISS'

    match_type = models.CharField(max_length=3)
    from_id = models.BigIntegerField()
    to_id = models.BigIntegerField()

    @classmethod
    def is_matched(cls, offer_id, issued_id):
        offer_match_exists = cls.objects.filter(
            match_type=cls.OFFER,
            from_id=offer_id,
            to_id=issued_id
        ).exists()

        issue_match_exists = cls.objects.filter(
            match_type=cls.ISSUE,
            from_id=issued_id,
            to_id=offer_id
        ).exists()

        return offer_match_exists and issue_match_exists
