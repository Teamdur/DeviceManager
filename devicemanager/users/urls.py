from django.urls import path

from devicemanager.users.views import theme_change_view

app_name = "users"

urlpatterns = [path("change-theme/", theme_change_view, name="change-theme")]
