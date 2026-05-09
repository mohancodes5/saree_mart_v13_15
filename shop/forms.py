from django import forms

from .models import Order, Product


class ProductSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(
            attrs={
                "class": "form-control rounded-pill border-0 bg-light px-4 py-2",
                "placeholder": "Search for sarees, silk, cotton…",
            }
        ),
    )


class AddToCartForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.HiddenInput())
    color = forms.CharField(required=False, widget=forms.HiddenInput())
    size = forms.CharField(required=False, widget=forms.HiddenInput())


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "full_name",
            "phone",
            "shipping_address",
            "city",
            "postal_code",
        )
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Full name"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone"}
            ),
            "shipping_address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Address"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "City"}
            ),
            "postal_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "PIN code"}
            ),
        }
