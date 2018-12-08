from rest_framework import serializers

from stats.models import UserRatingSummary


class UserRatingSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRatingSummary
        fields = (
            "id",
            "date",
            "rating",
            "user",
            "debts_count",
            "total_debt",
            "income",
        )
