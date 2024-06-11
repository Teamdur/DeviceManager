from django.urls import path

from devicemanager.users.views import obtain_auth_token_view, theme_change_view

app_name = "users"

urlpatterns = [
    path("change-theme/", theme_change_view, name="change-theme"),
    path("api-token/", obtain_auth_token_view, name="api-token"),
]
