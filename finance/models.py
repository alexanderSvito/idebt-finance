from enum import Enum

from django.db import models, DatabaseError, transaction
from django.conf import settings

from finance.exceptions import TransferError
from idebt.helpers import get_days_from_to_date, get_admin
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


class Issue(models.Model):
    borrower = models.ForeignKey(User, related_name='issues', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    max_overpay = models.DecimalField(decimal_places=2, max_digits=10)
    min_credit_period = models.IntegerField()
    fulfilled = models.BooleanField(default=False)

    @property
    def ready_for_auction(self):
        return len(self.buyers) >= settings.MIN_BUYERS_TRESHOLD

    def worth_function(self, offer):
        """ TODO: Better worth calculations """
        return offer.overpay_for(self.min_credit_period + 3)

    def run_auction(self):
        rank = sorted(self.buyers, key=self.worth_function)
        return rank[1]

    def get_offers(self):
        possible_offers = Offer.objects.filter(
            min_loan_size__lte=self.amount,
            max_loan_size__gte=self.amount,
            return_period__gte=self.min_credit_period
        )
        return [
            offer
            for offer in possible_offers
            if offer.overpay_for(self.amount) <= self.max_overpay
            and not offer.dried
            and not Match.objects.filter(
                match_type=Match.ISSUE,
                from_id=self.id,
                to_id=offer.id
            ).exists()
        ]

    def to_json(self):
        return {
            'desired_size': self.amount,
            'max_overpay': self.max_overpay,
            'min_credit_period': self.min_credit_period
        }


class Offer(AbstractLoan):
    creditor = models.ForeignKey(User, related_name='offers', on_delete=models.CASCADE)
    credit_fund = models.DecimalField(decimal_places=2, max_digits=10)
    used_funds = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    min_loan_size = models.DecimalField(decimal_places=2, max_digits=10)
    max_loan_size = models.DecimalField(decimal_places=2, max_digits=10)
    lots = models.ManyToManyField(Issue, related_name='buyers', on_delete=models.CASCADE)

    @property
    def dried(self):
        return self.credit_fund - self.used_funds < self.min_loan_size

    def overpay_for(self, loan_size):
        percent_days = self.return_period - self.grace_period
        if self.is_with_capitalization:
            return loan_size * (1 + self.credit_percentage) ** percent_days
        else:
            return loan_size * (1 + percent_days * self.credit_percentage)

    def get_issues(self):
        possible_issues = Issue.objects.filter(
            fulfilled=False,
            amount__lte=self.max_loan_size,
            amount__gte=self.min_loan_size,
            min_credit_period__lte=self.return_period
        )
        return [
            issue
            for issue in possible_issues
            if self.overpay_for(issue.amount) <= issue.max_overpay
            and not Match.objects.filter(
                match_type=Match.OFFER,
                from_id=issue.id,
                to_id=self.id
            ).exists()
        ]

    def freeze_funds(self, amount):
        used_funds = self.used_funds - amount
        self.used_funds = used_funds
        self.save()

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

    def _count_size_for_days(self, days):
        if self.is_with_capitalization:
            return self.loan_size * (1 + self.credit_percentage) ** days
        else:
            return self.loan_size * (1 + days * self.credit_percentage)

    @property
    def current_size(self):
        days_passed = get_days_from_to_date(self.created_at)
        return self._count_size_for_days(days_passed)

    @property
    def is_repayable(self):
        return self.current_size <= self.borrower.balance.balance

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
        offer = Offer.objects.get(pk=offer_id)
        issue = Issue.objects.get(pk=issue_id)
        debt = cls.objects.create(
            creditor=offer.creditor,
            borrower=issue.borrower,
            loan_size=issue.amount,
            credit=offer,
            credit_percentage=offer.credit_percentage,
            is_with_capitalization=offer.is_with_capitalization,
            grace_period=offer.grace_period,
            return_period=offer.return_period
        )
        offer.freeze_funds(issue.amount)
        debt.issue_funds()
        issue.fulfilled = True
        issue.save()
        issue.borrower.save()
        offer.creditor.save()
        return debt

    def transfer_funds(self, sender, receiver, amount):
        try:
            with transaction.atomic():
                sender.balance.balance -= amount
                receiver.balance.balance += amount
                sender.balance.save()
                receiver.balance.save()
                sender.save()
                receiver.save()
                self.save()
        except DatabaseError as e:
            raise TransferError("Can't transfer funds") from e

    def issue_funds(self):
        amount = self.loan_size
        self.transfer_funds(
            self.creditor,
            self.borrower,
            amount
        )

    def repay_funds(self):
        amount_for_creditor, amount_for_us = self.split_profit()
        admin = get_admin()
        with transaction.atomic():
            self.transfer_funds(
                self.borrower,
                self.creditor,
                amount_for_creditor
            )
            self.transfer_funds(
                self.borrower,
                admin,
                amount_for_us
            )

    def split_profit(self):
        profit = self.current_size - self.loan_size
        our_profit = profit * settings.SHARE_PERCENTAGE
        creditor_profit = profit * (1 - settings.SHARE_PERCENTAGE)
        return self.loan_size + creditor_profit, our_profit

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
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def is_matched(cls, offer_id, issue_id):
        offer_match_exists = cls.objects.filter(
            match_type=cls.OFFER,
            from_id=offer_id,
            to_id=issue_id
        ).exists()

        issue_match_exists = cls.objects.filter(
            match_type=cls.ISSUE,
            from_id=issue_id,
            to_id=offer_id
        ).exists()

        return offer_match_exists and issue_match_exists
