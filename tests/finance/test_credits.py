from decimal import Decimal

from finance.models import Debt
from finance.serializers import IssueSerializer, OfferSerializer, MatchSerializer
from tests.abstract import AbstractTestCase
from users.models import User


class CreditsTestCase(AbstractTestCase):
    def test_we_create_a_debt_with_match(self):
        creditor = self.get_creditor_with_balance(1500)
        borrower = self.get_borrower()

        initial_borrower_balance = Decimal(borrower.balance.balance)
        initial_creditor_balance = Decimal(creditor.balance.balance)

        good_offer = OfferSerializer(data={
            'credit_fund': 1500,
            'min_loan_size': 200,
            'max_loan_size': 300,
            'credit_percentage': 0.01,
            'return_period': 25,
            'creditor': creditor.id
        })  # Good, but fits in overpay with max
        good_offer.is_valid(raise_exception=True)
        good_offer = good_offer.save()

        good_issue = IssueSerializer(data={
            "borrower": borrower.id,
            "amount": 200,
            "max_overpay": 250,
            "min_credit_period": 15
        })
        good_issue.is_valid(raise_exception=True)
        good_issue = good_issue.save()

        match = MatchSerializer(data={
            'match_type': "OFF",
            'from_id': good_offer.id,
            'to_id': good_issue.id,
        })
        match.is_valid(raise_exception=True)
        match, is_matched = match.save()

        self.assertFalse(is_matched)

        match = MatchSerializer(data={
            'match_type': "ISS",
            'from_id': good_issue.id,
            'to_id': good_offer.id,
        })
        match.is_valid(raise_exception=True)
        match, is_matched = match.save()

        self.assertTrue(is_matched)

        debt = Debt.objects.get(creditor_id=creditor.id, borrower_id=borrower.id)
        self.assertIsNotNone(debt)

        borrower = User.objects.get(pk=borrower.id)
        creditor = User.objects.get(pk=creditor.id)

        self.assertAlmostEqual(
            initial_borrower_balance + debt.loan_size,
            borrower.balance.balance,
            2,
            msg='Funds not transferred'
        )

        self.assertAlmostEqual(
            initial_creditor_balance - debt.loan_size,
            creditor.balance.balance,
            2,
            msg='Funds not transferred'
        )
