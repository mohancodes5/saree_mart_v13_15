from django.contrib.auth.mixins import UserPassesTestMixin


class VendorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (getattr(u, "is_vendor", False) or u.is_superuser)

    login_url = "/accounts/vendor/login/"
    raise_exception = False
