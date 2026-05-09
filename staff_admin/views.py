from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import logout
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DeleteView, ListView, RedirectView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from shop.models import Category, Order, Product, ProductImage

from .forms import CategoryForm, StaffOrderStatusForm, StaffProductForm
from .mixins import StaffRequiredMixin


class StaffLoginRedirectView(RedirectView):
    """`/manage/login/` -> store login with return URL to site admin."""

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return f"{reverse('accounts:login')}?{urlencode({'next': reverse('staff_admin:home')})}"


class StaffLogoutView(View):
    """GET-friendly logout (same session as store); then normal login page."""

    def get(self, request):
        logout(request)
        return redirect(reverse("accounts:login"))


class StaffHomeView(StaffRequiredMixin, TemplateView):
    template_name = "staff_admin/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["product_count"] = Product.objects.count()
        ctx["order_count"] = Order.objects.count()
        ctx["category_count"] = Category.objects.count()
        return ctx


class StaffCategoryListView(StaffRequiredMixin, ListView):
    model = Category
    template_name = "staff_admin/category_list.html"
    context_object_name = "categories"


class StaffCategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "staff_admin/category_form.html"
    success_url = reverse_lazy("staff_admin:categories")

    def form_valid(self, form):
        messages.success(self.request, "Category created.")
        return super().form_valid(form)


class StaffCategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "staff_admin/category_form.html"
    success_url = reverse_lazy("staff_admin:categories")

    def form_valid(self, form):
        messages.success(self.request, "Category updated.")
        return super().form_valid(form)


class StaffCategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = "staff_admin/category_confirm_delete.html"
    success_url = reverse_lazy("staff_admin:categories")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Category removed.")
        except ProtectedError:
            messages.error(
                request,
                "Cannot delete: products still use this category. Remove or reassign them first.",
            )
        return HttpResponseRedirect(self.get_success_url())


class StaffProductListView(StaffRequiredMixin, ListView):
    model = Product
    template_name = "staff_admin/product_list.html"
    context_object_name = "products"
    paginate_by = 30

    def get_queryset(self):
        return (
            Product.objects.select_related("category", "vendor")
            .prefetch_related("images")
            .order_by("-updated_at")
        )


class StaffProductCreateView(StaffRequiredMixin, CreateView):
    model = Product
    form_class = StaffProductForm
    template_name = "staff_admin/product_form.html"
    success_url = reverse_lazy("staff_admin:products")

    def form_valid(self, form):
        self.object = form.save()
        self._save_images(self.object)
        messages.success(self.request, "Saree listing published.")
        return HttpResponseRedirect(self.get_success_url())

    def _save_images(self, product):
        files = self.request.FILES.getlist("images")
        for i, f in enumerate(files):
            if f:
                ProductImage.objects.create(
                    product=product, image=f, sort_order=i
                )


class StaffProductUpdateView(StaffRequiredMixin, UpdateView):
    model = Product
    form_class = StaffProductForm
    template_name = "staff_admin/product_form.html"
    success_url = reverse_lazy("staff_admin:products")

    def get_queryset(self):
        return Product.objects.all()

    def form_valid(self, form):
        messages.success(self.request, "Listing updated.")
        response = super().form_valid(form)
        files = self.request.FILES.getlist("images")
        start = self.object.images.count()
        for i, f in enumerate(files):
            if f:
                ProductImage.objects.create(
                    product=self.object, image=f, sort_order=start + i
                )
        return response


class StaffProductDeleteView(StaffRequiredMixin, DeleteView):
    model = Product
    template_name = "staff_admin/product_confirm_delete.html"
    success_url = reverse_lazy("staff_admin:products")

    def get_queryset(self):
        return Product.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Product removed from catalogue.")
        return super().delete(request, *args, **kwargs)


class StaffOrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = "staff_admin/order_list.html"
    context_object_name = "orders"
    paginate_by = 30

    def get_queryset(self):
        return (
            Order.objects.select_related("user")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Order.Status.choices
        return ctx


class StaffOrderStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = Order.objects.filter(pk=pk).first()
        if not order:
            messages.error(request, "Order not found.")
            return redirect("staff_admin:orders")
        form = StaffOrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order status updated.")
        else:
            messages.error(request, "Invalid status.")
        return redirect("staff_admin:orders")
