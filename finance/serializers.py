from rest_framework import serializers
from finance.models import Offer, Issue, Debt, Match
from users.models import User


class OfferSerializer(serializers.ModelSerializer):
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
        )

    def validate_credit_fund(self, value):
        user = User.objects.get(pk=self.initial_data['creditor'])
        if value > user.balance.balance:
            raise serializers.ValidationError("Can't make credit fund bigger than user's balance")
        return value


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            'id',
            'borrower',
            'amount',
            'max_overpay',
            'min_credit_period',
        )


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
            'is_with_capitalization'
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
            Debt.create_from(offer_id, issue_id)
            return match, True
        else:
            return match, False
