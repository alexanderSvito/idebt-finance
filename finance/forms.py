from django.forms import ModelForm
from finance.models import Offer, Issue, Match


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        fields = ['credit_fund', 'min_loan_size', 'max_loan_size', 'credit_percentage',
                  'is_with_capitalization', 'grace_period', 'return_period']


class IssueForm(ModelForm):
    class Meta:
        model = Issue
        fields = ['amount', 'max_overpay', 'max_credit_period']


class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = ['match_type', 'from_id', 'to_id']