from django.forms import ModelForm
from finance.models import Offer


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        fields = ['credit_fund', 'min_loan_size', 'max_loan_size', 'credit_percentage',
                  'is_with_capitalization', 'grace_period', 'return_period']
