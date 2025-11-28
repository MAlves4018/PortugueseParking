from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()  # isto vai ser customers.Customer

class CustomerRegistrationForm(UserCreationForm):
    ssn = forms.CharField(
        max_length=50,
        required=False,
        help_text="Social security number or equivalent identifier.",
    )
    billing_info = forms.CharField(
        required=False,
        widget=forms.Textarea,
        help_text="Optional billing information.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "ssn", "billing_info")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        user.ssn = self.cleaned_data.get("ssn", "")
        user.billing_info = self.cleaned_data.get("billing_info", "")

        if commit:
            user.save()
        return user
