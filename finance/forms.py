from django.forms import ModelForm
from finance.models import Offer, Issue, Match, Debt


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        fields = ['credit_fund', 'min_loan_size', 'max_loan_size', 'credit_percentage',
                  'is_with_capitalization', 'grace_period', 'return_period']


class IssueForm(ModelForm):
    class Meta:
        model = Issue
        fields = ['amount', 'max_overpay', 'min_credit_period']


class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = ['match_type', 'from_id', 'to_id']

    def save(self, commit=True):
        match = super(ModelForm, self).save(commit)
        if match.match_type == 'OFF':
            offer_id = match.from_id
            issue_id = match.to_id
        else:
            offer_id = match.to_id
            issue_id = match.from_id
        if Match.is_matched(offer_id, issue_id):
            debt = Debt.create_from(offer_id, issue_id)
            return match, True, debt
        else:
            return match, False, None
