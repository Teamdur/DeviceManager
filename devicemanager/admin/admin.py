from django.contrib.admin import AdminSite
from django.http import HttpRequest


class AppAdminSite(AdminSite):
    def has_permission(self, request: HttpRequest) -> bool:
        return request.user.is_active
