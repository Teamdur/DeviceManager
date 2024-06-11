from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import JSONParser

from devicemanager.users.forms import ColorThemeChangeForm
from devicemanager.users.user_preferences import UserPreferences


class ThemeChange(View):
    @staticmethod
    def post(request: HttpRequest) -> HttpResponse:
        form = ColorThemeChangeForm(request.POST)
        if form.is_valid():
            theme = form.cleaned_data["theme"]
            user_preferences = UserPreferences(request=request)
            user_preferences.theme = theme
            user_preferences.save()
        return redirect(request.headers.get("referer", reverse("admin:index")))


theme_change_view = ThemeChange.as_view()


class CustomAuthToken(ObtainAuthToken):
    parser_classes = [JSONParser]


obtain_auth_token_view = CustomAuthToken.as_view()
