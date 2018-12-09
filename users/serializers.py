import functools

from rest_framework import serializers
from rest_framework_jwt.compat import PasswordField

from finance.models import Debt
from users.models import User, Balance

from django.contrib.auth.hashers import make_password


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ('balance', )


class UserSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(source='balance.balance', decimal_places=2, max_digits=30, required=False)
    debt_outstanding_amount = serializers.SerializerMethodField()
    interest_amount = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "passport_number",
            "telephone",
            "email",
            "rating",
            "balance",
            "emp_title",
            "annual_income",
            "is_creditor",
            "is_locked",
            "date_joined",
            "debt_outstanding_amount",
            "interest_amount",
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')

        return value

    def get_debt_outstanding_amount(self, obj):
        debts = Debt.objects.filter(borrower=obj, is_closed=False)
        return functools.reduce(lambda x, y: x + y.current_size, debts, 0) if debts else 0

    def get_interest_amount(self, obj):
        debts = Debt.objects.filter(borrower=obj, is_closed=False)
        if not debts:
            return 0

        outstanding = functools.reduce(lambda x, y: x + y.current_size, debts, 0) if debts else 0
        initial_loans = functools.reduce(lambda x, y: x + y.loan_size, debts, 0) if debts else 0
        return outstanding - initial_loans

    def create(self, validated_data):
        if 'balance' in validated_data:
            if 'id' in validated_data:
                instance = Balance.objects.get(owner_id=validated_data['id']['id'])
            else:
                instance = None
            balance = BalanceSerializer(instance=instance, data={'balance': validated_data['balance']['balance']})
            balance.is_valid(raise_exception=True)
            balance = balance.save()
            validated_data['balance'] = balance

        else:
            if 'id' not in validated_data:
                balance = BalanceSerializer(data={'balance': 0})
                balance.is_valid(raise_exception=True)
                balance = balance.save()
                validated_data['balance'] = balance

        user = super(UserSerializer, self).create(validated_data)

        return user


class ShallowUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "rating",
            "emp_title",
            "is_creditor",
            "is_locked",
            "complete"
        )


class PasswordSerializer(serializers.Serializer):
    current_password = PasswordField(required=False)
    password = PasswordField()
    password_confirmation = PasswordField(required=False)

    def validate_current_password(self, value):
        current_user = self.context.get('current_user')

        if current_user and not current_user.check_password(value):
            raise serializers.ValidationError('Invalid password')

        return value

    def validate_password_confirmation(self, value):
        current_user = self.context.get('current_user')

        if current_user and value != self.initial_data['password']:
            raise serializers.ValidationError('Passwords should be equals')

        return value

    def create(self, validated_data):
        return make_password(validated_data['password'], salt=None)

    def update(self, instance, validated_data):
        instance['password'] = make_password(validated_data['password'])
