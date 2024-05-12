from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path("oauth2/accounts/", include("allauth.urls")),
    path("users/", include("devicemanager.users.urls", namespace="users")),
    path("inventory/", include("devicemanager.inventory.urls", namespace="inventory")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("", admin.site.urls),
]
