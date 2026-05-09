from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DeleteView, ListView, TemplateView, UpdateView
from django.views.generic.edit import CreateView

from shop.models import Order, Product, ProductImage

from .forms import OrderStatusForm, VendorProductForm

from .mixins import VendorRequiredMixin


class DashboardHomeView(VendorRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_superuser:
            ctx["product_count"] = Product.objects.count()
            ctx["open_orders"] = Order.objects.exclude(
                status=Order.Status.DELIVERED
            ).count()
        else:
            ctx["product_count"] = Product.objects.filter(vendor=user).count()
            ctx["open_orders"] = (
                Order.objects.filter(items__product__vendor=user)
                .exclude(status=Order.Status.DELIVERED)
                .distinct()
                .count()
            )
        return ctx


class StockListView(VendorRequiredMixin, ListView):
    template_name = "dashboard/stock_list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        qs = Product.objects.select_related("category").prefetch_related("images")
        if not user.is_superuser:
            qs = qs.filter(vendor=user)
        return qs.order_by("-updated_at")


class ProductCreateView(VendorRequiredMixin, CreateView):
    model = Product
    form_class = VendorProductForm
    template_name = "dashboard/product_form.html"
    success_url = reverse_lazy("dashboard:stock")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.vendor = self.request.user
        self.object.save()
        self._save_images(self.object)
        messages.success(self.request, "Product created.")
        return HttpResponseRedirect(self.get_success_url())

    def _save_images(self, product):
        files = self.request.FILES.getlist("images")
        for i, f in enumerate(files):
            if f:
                ProductImage.objects.create(
                    product=product, image=f, sort_order=i
                )


class ProductUpdateView(VendorRequiredMixin, UpdateView):
    model = Product
    form_class = VendorProductForm
    template_name = "dashboard/product_form.html"
    success_url = reverse_lazy("dashboard:stock")

    def get_queryset(self):
        user = self.request.user
        qs = Product.objects.all()
        if not user.is_superuser:
            qs = qs.filter(vendor=user)
        return qs

    def form_valid(self, form):
        messages.success(self.request, "Product updated.")
        response = super().form_valid(form)
        files = self.request.FILES.getlist("images")
        start = self.object.images.count()
        for i, f in enumerate(files):
            if f:
                ProductImage.objects.create(
                    product=self.object, image=f, sort_order=start + i
                )
        return response


class ProductDeleteView(VendorRequiredMixin, DeleteView):
    model = Product
    template_name = "dashboard/product_confirm_delete.html"
    success_url = reverse_lazy("dashboard:stock")

    def get_queryset(self):
        user = self.request.user
        qs = Product.objects.all()
        if not user.is_superuser:
            qs = qs.filter(vendor=user)
        return qs

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Product removed.")
        return super().delete(request, *args, **kwargs)


class OrderListView(VendorRequiredMixin, ListView):
    template_name = "dashboard/order_list.html"
    context_object_name = "orders"
    paginate_by = 25

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Order.Status.choices
        return ctx

    def get_queryset(self):
        user = self.request.user
        qs = (
            Order.objects.select_related("user")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )
        if not user.is_superuser:
            qs = qs.filter(items__product__vendor=user).distinct()
        return qs


class OrderQuickStatusView(VendorRequiredMixin, View):
    """POST-only: update status from orders table dropdown."""

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        user = request.user
        if not user.is_superuser:
            if not order.items.filter(product__vendor=user).exists():
                from django.core.exceptions import PermissionDenied

                raise PermissionDenied
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order status updated.")
        else:
            messages.error(request, "Could not update status.")
        return redirect("dashboard:orders")
