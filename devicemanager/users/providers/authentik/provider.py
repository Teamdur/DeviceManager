from allauth.socialaccount.providers.github.provider import GitHubProvider


class AuthentikProvider(GitHubProvider):
    id = "authentik"
    name = "Authentik"


provider_classes = [AuthentikProvider]
