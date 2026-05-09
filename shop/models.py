from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Saree materials / types: Silk, Cotton, Georgette, etc."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    colors = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated (e.g. Red, Maroon, Gold)",
    )
    sizes = models.CharField(
        max_length=200,
        default="Free Size",
        help_text="Comma-separated sizes or single value",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", kwargs={"slug": self.slug})

    @property
    def effective_price(self):
        if self.discounted_price is not None and self.discounted_price < self.price:
            return self.discounted_price
        return self.price

    @property
    def discount_percent(self):
        if self.discounted_price is not None and self.discounted_price < self.price:
            p = float(self.price)
            if p <= 0:
                return 0
            return int(round((1 - float(self.discounted_price) / p) * 100))
        return 0

    @property
    def display_colors(self):
        if not self.colors:
            return []
        return [c.strip() for c in self.colors.split(",") if c.strip()]

    @property
    def display_sizes(self):
        if not self.sizes:
            return ["Free Size"]
        return [s.strip() for s in self.sizes.split(",") if s.strip()]


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/%Y/%m/")
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    shipping_address = models.TextField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} — {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=80, blank=True)
    size = models.CharField(max_length=80, blank=True)

    @property
    def line_total(self):
        return self.unit_price * self.quantity
