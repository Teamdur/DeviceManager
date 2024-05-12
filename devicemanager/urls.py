from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path("oauth2/accounts/", include("allauth.urls")),
    path("users/", include("devicemanager.users.urls", namespace="users")),
    path("", admin.site.urls),
]
