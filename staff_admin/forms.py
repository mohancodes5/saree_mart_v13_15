from django import forms

from dashboard.forms import VendorProductForm
from shop.models import Category, Order


class StaffProductForm(VendorProductForm):
    """Catalogue fields only; vendor is set automatically to the staff user posting."""

    class Meta(VendorProductForm.Meta):
        fields = (
            "name",
            "slug",
            "description",
            "price",
            "discounted_price",
            "category",
            "stock_quantity",
            "colors",
            "sizes",
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "slug")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
        }


class StaffOrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("status",)
        widgets = {
            "status": forms.Select(attrs={"class": "form-select form-select-sm"}),
        }
