from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("cart/add/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("buy-now/", views.BuyNowView.as_view(), name="buy_now"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/update/", views.UpdateCartView.as_view(), name="cart_update"),
    path("cart/remove/", views.RemoveFromCartView.as_view(), name="cart_remove"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("order/thanks/", views.OrderThanksView.as_view(), name="order_thanks"),
    path("my-orders/", views.MyOrdersView.as_view(), name="my_orders"),
]
