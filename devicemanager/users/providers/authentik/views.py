from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)

from devicemanager.users.providers.authentik.provider import AuthentikProvider


class AuthentikOAuth2Adapter(GitHubOAuth2Adapter):
    provider_id = AuthentikProvider.id
    settings = app_settings.PROVIDERS.get(provider_id, {})

    if "AUTHENTIK_URL" in settings:
        web_url = settings.get("AUTHENTIK_URL").rstrip("/")
        api_url = "{0}/api/v3".format(web_url)
    else:
        web_url = "https://auth.wfis.lol"
        api_url = web_url

    access_token_url = "{0}/login/oauth/access_token".format(web_url)
    authorize_url = "{0}/login/oauth/authorize".format(web_url)
    profile_url = "{0}/user".format(api_url)
    emails_url = "{0}/user/emails".format(api_url)

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {}".format(token.token)}
        resp = get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()
        if app_settings.QUERY_EMAIL and not extra_data.get("email"):
            extra_data["email"] = self.get_email(headers)
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(AuthentikOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AuthentikOAuth2Adapter)
