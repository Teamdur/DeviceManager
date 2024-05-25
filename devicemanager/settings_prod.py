import environ

from devicemanager.settings import *  # noqa

env = environ.Env(
    SECRET_KEY=(str, "django-insecure-&#w*b7*0v3z4z62l989)sjk6wqdj_%v-)ty(7iakr+nw9&4i(%"),
    EMAIL_BACKEND=(str, "django.core.mail.backends.filebased.EmailBackend"),
)

DEBUG = False
ALLOWED_HOSTS = ["*"]
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
CSRF_TRUSTED_ORIGINS = ["https://devicemanager.homa-server.eu", "https://device-manager.critteros.dev"]

SECRET_KEY = env("SECRET_KEY")

EMAIL_BACKEND = env("EMAIL_BACKEND")  # noqa: F405

if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    EMAIL_HOST = env("EMAIL_HOST")  # noqa: F405
    EMAIL_PORT = env("EMAIL_PORT")  # noqa: F405
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")  # noqa: F405
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")  # noqa: F405
    EMAIL_USE_SSL = env("EMAIL_USE_SSL", None)  # noqa: F405
    if EMAIL_USE_SSL and EMAIL_USE_SSL.lower() == "false":
        EMAIL_USE_SSL = None
    EMAIL_USE_TLS = env("EMAIL_USE_TLS", None)  # noqa: F405
    if EMAIL_USE_TLS and EMAIL_USE_TLS.lower() == "false":
        EMAIL_USE_TLS = None

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
