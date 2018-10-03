from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "balance",
            "rating",
            "emp_title",
            "annual_income",
            "is_creditor",
            "is_locked",
        )
