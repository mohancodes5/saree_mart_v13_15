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
    path("dashboard/", include("dashboard.urls")),
    path("", include("shop.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production (e.g. Render): django.conf.urls.static.static() only wires media when DEBUG=True,
    # so we serve uploads explicitly. For durability across deploys, use a persistent disk or S3.
    media_url = settings.MEDIA_URL.lstrip("/")
    urlpatterns += [
        re_path(
            rf"^{media_url}(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
