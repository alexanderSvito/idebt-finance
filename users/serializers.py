from django.db import transaction
from rest_framework import serializers
from rest_framework_jwt.compat import PasswordField

from users.models import User, Balance

from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(source='balance.balance', decimal_places=2, max_digits=30)

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
        )

    def create(self, validated_data):
        if 'balance' in validated_data:
            del validated_data['balance']
            user = super(UserSerializer, self).create(validated_data)
            balance = Balance.objects.create(owner=user)
            user.balance = balance
            user.save()
        else:
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
        )


class PasswordSerializer(serializers.Serializer):
    password = PasswordField()

    def create(self, validated_data):
        return make_password(validated_data['password'], salt=None)

    def update(self, instance, validated_data):
        instance['password'] = make_password(validated_data['password'])
