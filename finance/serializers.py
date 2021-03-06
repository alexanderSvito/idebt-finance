from decimal import Decimal

from rest_framework import serializers
from finance.documents.generator import create_document
from finance.models import Offer, Issue, Debt, Match
from users.models import User


class OfferSerializer(serializers.ModelSerializer):
    credit_fund = serializers.DecimalField(max_digits=6, decimal_places=2)
    credit_percentage = serializers.DecimalField(decimal_places=2, max_digits=5, min_value=0, max_value=100)
    grace_period = serializers.IntegerField(min_value=0, max_value=365)
    return_period = serializers.IntegerField(min_value=0, max_value=365)

    class Meta:
        model = Offer
        fields = (
            'id',
            'creditor',
            'credit_fund',
            'min_loan_size',
            'max_loan_size',
            'credit_percentage',
            'is_with_capitalization',
            'grace_period',
            'return_period',
            'used_funds',
            'is_closed'
        )

    def validate_credit_fund(self, value):
        user = User.objects.get(pk=self.initial_data['creditor'])
        if value > user.balance.balance:
            raise serializers.ValidationError("Can't make credit fund bigger than user's balance.")
        return value

    def validate_min_loan_size(self, value):
        if value > Decimal(self.initial_data['credit_fund']):
            raise serializers.ValidationError("Can't make min loan size bigger than credit fund.")
        return value

    def validate_max_loan_size(self, value):
        if value > Decimal(self.initial_data['credit_fund']):
            raise serializers.ValidationError("Can't make max loan size bigger than credit fund.")
        return value


class IssueSerializer(serializers.ModelSerializer):
    borrower_stats = serializers.SerializerMethodField()
    amount = serializers.DecimalField(max_digits=6, decimal_places=2)
    max_overpay = serializers.DecimalField(max_digits=8, decimal_places=2)
    min_credit_period = serializers.IntegerField(min_value=0, max_value=365)

    class Meta:
        model = Issue
        fields = (
            'id',
            'borrower',
            'borrower_stats',
            'amount',
            'max_overpay',
            'min_credit_period',
            'fulfilled'
        )

    def validate_max_overpay(self, value):
        if value < Decimal(self.initial_data['amount']):
            raise serializers.ValidationError("Overpay can't be smaller than initial credit amount.")
        return value

    def get_borrower_stats(self, obj):
        return {'rating': obj.borrower.rating}


class DebtSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='status.value')

    current_size = serializers.DecimalField(max_digits=20, decimal_places=2)
    size_in_week = serializers.DecimalField(max_digits=20, decimal_places=2)
    size_in_month = serializers.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        model = Debt
        fields = (
            'id',
            'status',
            'loan_size',
            'current_size',
            'size_in_week',
            'size_in_month',
            'credit_percentage',
            'created_at',
            'is_with_capitalization',
        )


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = (
            'match_type',
            'from_id',
            'to_id',
        )

    def create(self, validated_data):
        match = Match.objects.create(**validated_data)
        if match.match_type == 'OFF':
            offer_id = match.from_id
            issue_id = match.to_id
        else:
            offer_id = match.to_id
            issue_id = match.from_id
        if Match.is_matched(offer_id, issue_id):
            issue = Issue.objects.get(pk=issue_id)
            offer = Offer.objects.get(pk=offer_id)
            issue.buyers.add(offer)
            issue.save()
            if issue.is_ready_for_auction:
                winner = issue.run_auction()
                debt = Debt.create_from(winner.id, issue_id)
                filename = create_document(debt)
                debt.contract_filename = filename
                debt.save()
                return match, True
            else:
                return match, False
        else:
            return match, False
