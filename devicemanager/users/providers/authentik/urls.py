from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import AuthentikProvider

urlpatterns = default_urlpatterns(AuthentikProvider)
