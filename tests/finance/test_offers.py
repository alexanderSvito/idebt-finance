from finance.serializers import OfferSerializer, IssueSerializer
from tests.abstract import AbstractTestCase


class OffersTestCase(AbstractTestCase):
    def test_we_cant_create_offer_with_incomplete_fields(self):
        creditor = self.get_creditor_with_balance(500)

        offer = OfferSerializer(data={
            'credit_fund': 500,
            'min_loan_size': 100,
            'max_loan_size': 200,
            'credit_percentage': 0.01,
            'creditor': creditor.id
        })
        offer.is_valid()

        self.assertHasError(
            offer,
            'return_period',
            'This field is required.'
        )

    def test_we_cant_create_offer_without_balance(self):
        creditor = self.get_creditor_with_balance(0)

        offer = OfferSerializer(data={
            'credit_fund': 1500,
            'min_loan_size': 100,
            'max_loan_size': 200,
            'credit_percentage': 0.01,
            'return_period': 30,
            'creditor': creditor.id
        })
        offer.is_valid()

        self.assertHasError(
            offer,
            'credit_fund',
            'Can\'t make credit fund bigger than user\'s balance.'
        )

    def test_we_filter_suitable_issues(self):
        creditor = self.get_creditor_with_balance(1500)
        borrower = self.get_borrower()

        good_issue = IssueSerializer(data={
            "borrower": borrower.id,
            "amount": 500,
            "max_overpay": 700,
            "min_credit_period": 7
        })
        good_issue.is_valid(raise_exception=True)
        good_issue = good_issue.save()

        bad_issue = IssueSerializer(data={
            "borrower": borrower.id,
            "amount": 900,
            "max_overpay": 1000,
            "min_credit_period": 5
        })  # Bigger then expected
        bad_issue.is_valid(raise_exception=True)
        bad_issue.save()

        bad_issue = IssueSerializer(data={
            "borrower": borrower.id,
            "amount": 100,
            "max_overpay": 110,
            "min_credit_period": 30
        })  # Smaller then expected
        bad_issue.is_valid(raise_exception=True)
        bad_issue.save()

        bad_issue = IssueSerializer(data={
            "borrower": borrower.id,
            "amount": 500,
            "max_overpay": 600,
            "min_credit_period": 7
        })  # Has smaller overpay
        bad_issue.is_valid(raise_exception=True)
        bad_issue.save()

        bad_issue = IssueSerializer(data={
            "borrower": borrower.id,
            "amount": 500,
            "max_overpay": 700,
            "min_credit_period": 7,
            "fulfilled": True
        })  # Fulfilled
        bad_issue.is_valid(raise_exception=True)
        bad_issue.save()

        bad_issue = IssueSerializer(data={
            "borrower": borrower.id,
            "amount": 500,
            "max_overpay": 800,
            "min_credit_period": 60
        })  # Has bigger credit period
        bad_issue.is_valid(raise_exception=True)
        bad_issue.save()

        offer = OfferSerializer(data={
            'credit_fund': 1500,
            'min_loan_size': 400,
            'max_loan_size': 600,
            'credit_percentage': 0.01,
            'return_period': 30,
            'creditor': creditor.id
        })
        offer.is_valid(raise_exception=True)
        offer = offer.save()

        issues = offer.get_issues()

        self.assertEqual(len(issues), 1)
        self.assertIn(good_issue, issues)
