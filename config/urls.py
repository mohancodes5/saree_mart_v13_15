from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView

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
