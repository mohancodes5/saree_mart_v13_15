from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),
    path("stock/", views.StockListView.as_view(), name="stock"),
    path("stock/add/", views.ProductCreateView.as_view(), name="product_add"),
    path("stock/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("stock/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    path("orders/", views.OrderListView.as_view(), name="orders"),
    path("orders/<int:pk>/status/", views.OrderQuickStatusView.as_view(), name="order_status"),
]
