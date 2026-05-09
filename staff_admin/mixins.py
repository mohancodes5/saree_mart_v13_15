from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy


class StaffRequiredMixin(UserPassesTestMixin):
    """Platform operators (is_staff). Not the same as vendor dashboard."""

    login_url = reverse_lazy("accounts:login")
    raise_exception = False

    def test_func(self):
        u = self.request.user
        return u.is_authenticated and u.is_active and u.is_staff

    def handle_no_permission(self):
        """
        Django's default raises 403 for authenticated users who fail the test.
        Redirect to staff login instead (no flash message — avoids looking like an error).
        """
        return redirect_to_login(
            self.request.get_full_path(),
            self.get_login_url(),
            self.get_redirect_field_name(),
        )
