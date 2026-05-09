from django.urls import path

from . import views

app_name = "staff_admin"

urlpatterns = [
    path("login/", views.StaffLoginRedirectView.as_view(), name="login"),
    path("logout/", views.StaffLogoutView.as_view(), name="logout"),
    path("", views.StaffHomeView.as_view(), name="home"),
    path("categories/", views.StaffCategoryListView.as_view(), name="categories"),
    path("categories/add/", views.StaffCategoryCreateView.as_view(), name="category_add"),
    path("categories/<int:pk>/edit/", views.StaffCategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", views.StaffCategoryDeleteView.as_view(), name="category_delete"),
    path("products/add/", views.StaffProductCreateView.as_view(), name="product_add"),
    path("products/<int:pk>/edit/", views.StaffProductUpdateView.as_view(), name="product_edit"),
    path("products/<int:pk>/delete/", views.StaffProductDeleteView.as_view(), name="product_delete"),
    path("products/", views.StaffProductListView.as_view(), name="products"),
    path("orders/", views.StaffOrderListView.as_view(), name="orders"),
    path("orders/<int:pk>/status/", views.StaffOrderStatusView.as_view(), name="order_status"),
]
