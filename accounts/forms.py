from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Username"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("email", "password1", "password2"):
            if name in self.fields:
                self.fields[name].widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_vendor = False
        if commit:
            user.save()
        return user


class VendorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("email", "password1", "password2"):
            if name in self.fields:
                self.fields[name].widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone", "")
        user.is_vendor = True
        if commit:
            user.save()
        return user
