from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, TemplateView

from . import cart as cart_util
from .forms import AddToCartForm, CheckoutForm, ProductSearchForm
from .models import Order, OrderItem, Product


class HomeView(TemplateView):
    template_name = "shop/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = Product.objects.select_related("category", "vendor").prefetch_related(
            "images"
        )
        category = self.request.GET.get("category")
        q = self.request.GET.get("q", "").strip()
        if category:
            qs = qs.filter(category__slug=category)
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(category__name__icontains=q)
            )
        from .models import Category

        ctx["products"] = qs[:48]
        ctx["categories"] = Category.objects.all()
        ctx["search_form"] = ProductSearchForm(self.request.GET or None)
        ctx["active_category"] = category
        ctx["search_q"] = q
        return ctx


class ProductDetailView(TemplateView):
    template_name = "shop/product_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = get_object_or_404(
            Product.objects.select_related("category", "vendor").prefetch_related(
                "images"
            ),
            slug=self.kwargs["slug"],
        )
        ctx["product"] = product
        ctx["add_form"] = AddToCartForm(
            initial={
                "product_id": product.id,
                "quantity": 1,
                "color": product.display_colors[0] if product.display_colors else "",
                "size": product.display_sizes[0] if product.display_sizes else "Free Size",
            }
        )
        return ctx


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        form = AddToCartForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Could not add to cart.")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        pid = form.cleaned_data["product_id"]
        qty = form.cleaned_data["quantity"]
        color = form.cleaned_data.get("color") or ""
        size = form.cleaned_data.get("size") or ""
        product = get_object_or_404(Product, pk=pid)
        if qty > product.stock_quantity:
            messages.error(request, "Not enough stock available.")
            return redirect(product.get_absolute_url())
        cart_util.add_item(request, pid, qty, color, size)
        messages.success(request, f"Added “{product.name}” to cart.")
        next_url = request.POST.get("next")
        if next_url == "checkout" and request.user.is_authenticated:
            return redirect(reverse("shop:checkout"))
        if next_url == "checkout" and not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={reverse('shop:checkout')}")
        return redirect(reverse("shop:cart"))


class BuyNowView(View):
    """Add single item and go to checkout (or login with next=checkout)."""

    def post(self, request, *args, **kwargs):
        form = AddToCartForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Could not process buy now.")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        pid = form.cleaned_data["product_id"]
        qty = form.cleaned_data["quantity"]
        color = form.cleaned_data.get("color") or ""
        size = form.cleaned_data.get("size") or ""
        product = get_object_or_404(Product, pk=pid)
        if qty > product.stock_quantity:
            messages.error(request, "Not enough stock available.")
            return redirect(product.get_absolute_url())
        cart_util.clear_cart(request)
        cart_util.add_item(request, pid, qty, color, size)
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={reverse('shop:checkout')}")
        return redirect(reverse("shop:checkout"))


class CartView(TemplateView):
    template_name = "shop/cart.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        raw = cart_util.get_cart(self.request)
        items = []
        subtotal = Decimal("0.00")
        for pid, data in raw.items():
            try:
                p = Product.objects.prefetch_related("images").get(pk=int(pid))
            except Product.DoesNotExist:
                continue
            q = int(data.get("qty", 1))
            line = p.effective_price * q
            subtotal += line
            items.append(
                {
                    "product": p,
                    "qty": q,
                    "color": data.get("color", ""),
                    "size": data.get("size", ""),
                    "line_total": line,
                }
            )
        ctx["cart_items"] = items
        ctx["subtotal"] = subtotal
        ctx["cart_empty"] = len(items) == 0
        return ctx


class UpdateCartView(View):
    def post(self, request, *args, **kwargs):
        pid = request.POST.get("product_id")
        qty = int(request.POST.get("quantity", 1))
        if pid:
            cart_util.update_qty(request, int(pid), qty)
        return redirect(reverse("shop:cart"))


class RemoveFromCartView(View):
    def post(self, request, *args, **kwargs):
        pid = request.POST.get("product_id")
        if pid:
            cart_util.remove_item(request, int(pid))
        return redirect(reverse("shop:cart"))


class CheckoutView(LoginRequiredMixin, FormView):
    template_name = "shop/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("shop:order_thanks")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not getattr(
            request.user, "email_verified", True
        ):
            messages.warning(
                request,
                "Please verify your email before checkout. Check your inbox for the link, "
                "or resend it from your profile.",
            )
            return redirect(reverse("accounts:profile"))
        if not cart_util.get_cart(request):
            return redirect("shop:cart")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        raw = cart_util.get_cart(self.request)
        if not raw:
            messages.error(self.request, "Your cart is empty.")
            return redirect("shop:cart")

        items_data = []
        total = Decimal("0.00")
        for pid, data in raw.items():
            try:
                p = Product.objects.get(pk=int(pid))
            except Product.DoesNotExist:
                continue
            q = int(data.get("qty", 1))
            if q > p.stock_quantity:
                messages.error(
                    self.request,
                    f"Not enough stock for {p.name}. Please update your cart.",
                )
                return redirect("shop:cart")
            line = p.effective_price * q
            total += line
            items_data.append(
                {
                    "product": p,
                    "qty": q,
                    "unit_price": p.effective_price,
                    "color": data.get("color", ""),
                    "size": data.get("size", ""),
                }
            )

        if not items_data:
            messages.error(self.request, "No valid items in cart.")
            return redirect("shop:cart")

        order = form.save(commit=False)
        order.user = self.request.user
        order.total_price = total
        order.status = Order.Status.PENDING
        order.save()

        for row in items_data:
            OrderItem.objects.create(
                order=order,
                product=row["product"],
                quantity=row["qty"],
                unit_price=row["unit_price"],
                color=row["color"],
                size=row["size"],
            )
            pr = row["product"]
            pr.stock_quantity -= row["qty"]
            pr.save(update_fields=["stock_quantity"])

        cart_util.clear_cart(self.request)
        self.request.session["last_order_id"] = order.id
        messages.success(self.request, "Order placed successfully.")
        return HttpResponseRedirect(self.get_success_url())


class OrderThanksView(LoginRequiredMixin, TemplateView):
    template_name = "shop/order_thanks.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        oid = self.request.session.get("last_order_id")
        ctx["order"] = None
        if oid:
            ctx["order"] = Order.objects.filter(
                pk=oid, user=self.request.user
            ).first()
        return ctx


class MyOrdersView(LoginRequiredMixin, ListView):
    template_name = "shop/my_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )
