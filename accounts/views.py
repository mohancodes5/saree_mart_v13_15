import secrets
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, TemplateView

from .email_utils import (
    issue_email_verification_token,
    send_verification_email,
)
from .forms import CustomerRegistrationForm
from .models import User


def _resend_api_key_configured():
    from django.conf import settings as dj_settings

    return bool((getattr(dj_settings, "RESEND_API_KEY", "") or "").strip())


class CustomerRegisterView(CreateView):
    model = User
    form_class = CustomerRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("shop:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        from django.contrib.auth import login

        user = self.object
        issue_email_verification_token(user)
        ok, api_msg = send_verification_email(self.request, user)
        if ok:
            messages.success(
                self.request,
                "Account created. Check your email and click the link to verify your address.",
            )
        elif api_msg:
            messages.warning(self.request, api_msg)
        elif not _resend_api_key_configured():
            messages.warning(
                self.request,
                "Account created, but we could not send a verification email "
                "(add RESEND_API_KEY to `.env`). You can resend from your profile later.",
            )
        else:
            messages.warning(
                self.request,
                "Account created, but we could not send the verification email. "
                "Try again from your profile.",
            )
        login(self.request, user)
        return response


class CustomerLoginView(auth_views.LoginView):
    """
    One login form for everyone.
    - Shoppers: Sign in / Sign up, then home or `next` (e.g. checkout).
    - Staff: use **Admin** or `/accounts/login/?next=/manage/`.
    """

    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        redirect_to = super().get_redirect_url()
        user = self.request.user
        if (
            redirect_to
            and "/manage" in redirect_to
            and not user.is_staff
        ):
            messages.warning(
                self.request,
                "That account cannot open Admin. Use an administrator username "
                "(e.g. from createsuperuser), or use User login for shopping.",
            )
            return reverse("shop:home")
        return redirect_to or self.get_default_redirect_url()

    def get_default_redirect_url(self):
        """When `next` is absent: staff → store admin panel; everyone else → shop."""
        user = self.request.user
        if user.is_staff:
            return reverse("staff_admin:home")
        return reverse("shop:home")


class LogoutView(View):
    """
    Log out via GET or POST. Django's built-in LogoutView often returns 405 on GET
    (logout links in the navbar use GET).
    """

    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect(reverse("shop:home"))

    def post(self, request):
        return self.get(request)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"


class VerifyEmailView(View):
    """One-click link from the verification email (Resend)."""

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, "That verification link is invalid.")
            return redirect(reverse("accounts:login"))

        if not user.email_verification_token or not secrets.compare_digest(
            user.email_verification_token, token
        ):
            messages.error(
                request,
                "That verification link is invalid or has already been used.",
            )
            return redirect(reverse("accounts:login"))

        user.email_verified = True
        user.email_verification_token = ""
        user.save(update_fields=["email_verified", "email_verification_token"])
        messages.success(request, "Your email has been verified.")
        next_url = request.GET.get("next") or reverse("shop:home")
        return redirect(next_url)


class ResendVerificationEmailView(LoginRequiredMixin, View):
    """POST from profile to send another verification email via Resend."""

    def post(self, request):
        user = request.user
        if user.email_verified:
            messages.info(request, "Your email is already verified.")
            return redirect(reverse("accounts:profile"))
        if not user.email:
            messages.error(request, "No email address on file.")
            return redirect(reverse("accounts:profile"))
        last = user.email_verification_sent_at
        if last and timezone.now() - last < timedelta(minutes=1):
            messages.warning(
                request,
                "Please wait a minute before requesting another verification email.",
            )
            return redirect(reverse("accounts:profile"))
        issue_email_verification_token(user)
        ok, api_msg = send_verification_email(request, user)
        if ok:
            messages.success(request, "Verification email sent. Check your inbox.")
        elif api_msg:
            messages.error(request, api_msg)
        elif not _resend_api_key_configured():
            messages.error(
                request,
                "Could not send email: RESEND_API_KEY is missing. Add it to `.env` next to "
                "`manage.py`, then restart the server.",
            )
        else:
            messages.error(
                request,
                "Could not send email. Check the server logs for details.",
            )
        return redirect(reverse("accounts:profile"))
