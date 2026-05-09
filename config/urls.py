from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

urlpatterns = [
    # Old /admin/ bookmarks -> custom admin (Django admin UI is disabled).
    path("admin/", RedirectView.as_view(url="/manage/", permanent=False)),
    path("manage/", include("staff_admin.urls")),
    path("accounts/", include("accounts.urls")),
    # Seller dashboard disabled — catalogue is managed via /manage/ only.
    re_path(
        r"^dashboard(?:/.*)?$",
        RedirectView.as_view(pattern_name="shop:home", permanent=False),
    ),
]

# Uploaded media MUST be registered before the catch-all `path("", include("shop.urls"))`,
# otherwise `/media/...` is handed to shop.urls and returns 404 (broken product images).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production (e.g. Render): static() returns [] when DEBUG=False; serve files explicitly.
    # For durability across deploys, add a Render Disk or use S3-compatible storage.
    media_url = settings.MEDIA_URL.lstrip("/")
    urlpatterns += [
        re_path(
            rf"^{media_url}(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

urlpatterns += [
    path("", include("shop.urls")),
]
