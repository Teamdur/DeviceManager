from django.contrib.admin import apps


class AppAdminConfig(apps.AdminConfig):
    default_site = "devicemanager.admin.admin.AppAdminSite"
