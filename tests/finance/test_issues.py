from finance.serializers import IssueSerializer, OfferSerializer
from tests.abstract import AbstractTestCase


class IssuesTestCase(AbstractTestCase):
    def test_we_cant_create_issue_with_incomplete_fields(self):
        borrower = self.get_borrower()

        issue = IssueSerializer(data={
            "borrower": borrower.id,
            "amount": 500,
            "max_overpay": 700
        })
        issue.is_valid()

        self.assertHasError(
            issue,
            'min_credit_period',
            'This field is required.'
        )

    def test_we_cant_create_issue_with_overpay_smaller_than_amount(self):
        borrower = self.get_borrower()

        offer = IssueSerializer(data={
            "borrower": borrower.id,
            "amount": 500,
            "max_overpay": 400,
            "min_credit_period": 7
        })
        offer.is_valid()

        self.assertHasError(
            offer,
            'max_overpay',
            'Overpay can\'t be smaller than initial credit amount.'
        )

    def test_we_filter_suitable_offers(self):
        creditor = self.get_creditor_with_balance(1500)
        borrower = self.get_borrower()

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

        bad_offer = OfferSerializer(data={
            'credit_fund': 1500,
            'min_loan_size': 1000,
            'max_loan_size': 1200,
            'credit_percentage': 0.07,
            'return_period': 30,
            'creditor': creditor.id
        })  # Bigger then expected
        bad_offer.is_valid(raise_exception=True)
        bad_offer.save()

        bad_offer = OfferSerializer(data={
            'credit_fund': 500,
            'min_loan_size': 10,
            'max_loan_size': 30,
            'credit_percentage': 0.1,
            'return_period': 4,
            'creditor': creditor.id
        })  # Smaller then expected
        bad_offer.is_valid(raise_exception=True)
        bad_offer.save()

        bad_offer = OfferSerializer(data={
            'credit_fund': 1500,
            'min_loan_size': 200,
            'max_loan_size': 300,
            'credit_percentage': 0.01,
            'return_period': 25,
            'is_with_capitalization': True,
            'creditor': creditor.id
        })  # Has bigger overpay
        bad_offer.is_valid(raise_exception=True)
        bad_offer.save()

        bad_offer = OfferSerializer(data={
            'credit_fund': 1500,
            'min_loan_size': 200,
            'max_loan_size': 300,
            'credit_percentage': 0.01,
            'return_period': 10,
            'creditor': creditor.id
        })  # Has smaller return period
        bad_offer.is_valid(raise_exception=True)
        bad_offer.save()

        bad_offer = OfferSerializer(data={
            'credit_fund': 1500,
            'min_loan_size': 200,
            'max_loan_size': 300,
            'credit_percentage': 0.01,
            'return_period': 20,
            'used_funds': 1450,
            'creditor': creditor.id
        })  # Dried all his funds
        bad_offer.is_valid(raise_exception=True)
        bad_offer.save()

        issue = IssueSerializer(data={
            "borrower": borrower.id,
            "amount": 200,
            "max_overpay": 250,
            "min_credit_period": 15
        })
        issue.is_valid(raise_exception=True)
        issue = issue.save()

        offers = issue.get_offers()

        self.assertEqual(len(offers), 1)
        self.assertIn(good_offer, offers)
