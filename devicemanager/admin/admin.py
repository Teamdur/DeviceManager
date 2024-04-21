from django.contrib.admin import AdminSite
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.urls import reverse


class AppAdminSite(AdminSite):
    def has_permission(self, request: HttpRequest) -> bool:
        # Allows anonymous users to login
        if request.path == reverse("admin:login") and isinstance(request.user, AnonymousUser):
            return False

        return True
