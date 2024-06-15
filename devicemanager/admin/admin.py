from allauth.socialaccount.providers import registry
from django.contrib.admin import AdminSite
from django.http import HttpRequest


class AppAdminSite(AdminSite):
    def has_permission(self, request: HttpRequest) -> bool:
        return request.user.is_active

    def each_context(self, request):
        ctx = super().each_context(request)
        ctx["socialaccount_providers"] = [provider.id for provider in registry.get_class_list()]
        return ctx
