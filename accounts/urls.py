from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.CustomerRegisterView.as_view(), name="register"),
    path(
        "vendor/register/",
        RedirectView.as_view(pattern_name="shop:home", permanent=False),
        name="vendor_register",
    ),
    path(
        "verify-email/<uidb64>/<token>/",
        views.VerifyEmailView.as_view(),
        name="verify_email",
    ),
    path(
        "resend-verification/",
        views.ResendVerificationEmailView.as_view(),
        name="resend_verification",
    ),
    path("login/", views.CustomerLoginView.as_view(), name="login"),
    path(
        "vendor/login/",
        RedirectView.as_view(pattern_name="accounts:login", permanent=False),
        name="vendor_login",
    ),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
