from django import forms
from django.contrib.auth import get_user_model

from dashboard.forms import VendorProductForm
from shop.models import Category, Order

User = get_user_model()


class StaffProductForm(VendorProductForm):
    """Same as vendor listing form, plus vendor assignment (site admin)."""

    class Meta(VendorProductForm.Meta):
        fields = (
            "name",
            "slug",
            "description",
            "price",
            "discounted_price",
            "category",
            "vendor",
            "stock_quantity",
            "colors",
            "sizes",
        )
        widgets = {
            **VendorProductForm.Meta.widgets,
            "vendor": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vendor"].queryset = User.objects.filter(is_vendor=True).order_by(
            "username"
        )
        self.fields["vendor"].empty_label = "Select seller account"
        if not self.fields["vendor"].queryset.exists():
            self.fields["vendor"].help_text = (
                "No vendor accounts yet. Register a seller or run: "
                "python manage.py seed_sample_sarees"
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
