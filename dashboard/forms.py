from django import forms
from django.utils.text import slugify

from shop.models import Order, Product


class VendorProductForm(forms.ModelForm):
    """Primary listing form; images uploaded separately via multi-file field."""

    slug = forms.SlugField(required=False)

    class Meta:
        model = Product
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
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "discounted_price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "stock_quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "colors": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Red, Maroon, Gold",
                }
            ),
            "sizes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Free Size or comma-separated",
                }
            ),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        if slug:
            return slug
        name = self.cleaned_data.get("name", "")
        base = slugify(name) or "product"
        candidate = base
        n = 1
        qs = Product.objects.all()
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        while qs.filter(slug=candidate).exists():
            candidate = f"{base}-{n}"
            n += 1
        return candidate


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("status",)
        widgets = {
            "status": forms.Select(attrs={"class": "form-select form-select-sm"}),
        }
