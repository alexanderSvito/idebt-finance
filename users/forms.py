import re

from django import forms
from users.models import User


class RegisterForm(forms.ModelForm):
    TELEPHONE_REGEX = re.compile(r'^\+\d{1,3}\(\d{1,3}\)\d{3}-\d{2}-\d{2}$', re.U)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "emp_title",
            "annual_income",
            "is_creditor",
            "password",
            "telephone"
        )

    def clean_telephone(self):
        telephone = self.cleaned_data.get("telephone")
        if not self.TELEPHONE_REGEX.match(telephone):
            raise forms.ValidationError(
                'Phone is in unknown format',
                code='telephone',
            )
        return telephone

    def clean_annual_income(self):
        annual_income = self.cleaned_data.get("annual_income")
        if annual_income < 0:
            raise forms.ValidationError(
                'Annual income can\'t be lower than zero',
                code='annual_income',
            )
        return annual_income

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
