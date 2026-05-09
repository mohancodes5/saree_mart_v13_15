from django.contrib import admin

from .models import Category, Order, OrderItem, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "vendor", "display_price", "stock_quantity")
    list_filter = ("category",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]

    @admin.display(description="Price")
    def display_price(self, obj):
        return f"₹{obj.effective_price}"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]
