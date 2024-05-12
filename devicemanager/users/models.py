from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from devicemanager.utils.fields import DictJSONField


class User(AbstractUser):
    room = models.CharField(max_length=100, blank=True)
    telephone_number = PhoneNumberField(blank=True, region="PL")
    website_url = models.URLField(blank=True)
    name_decoration = models.ForeignKey(
        "DisplayNameDecorator",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users",
        verbose_name=_("Degree"),
    )
    user_preferences = DictJSONField(_("User preferences"), default=dict)

    def get_name_decoration(self) -> str:
        return getattr(self.name_decoration, "decorator", "")

    def get_display_name(self) -> str:
        if not (self.first_name or self.last_name):
            return self.username

        if self.name_decoration:
            return f"{self.get_name_decoration()} {self.get_full_name()}"
        return self.get_full_name()


class DisplayNameDecorator(models.Model):
    decorator = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = _("display name decorator")
        verbose_name_plural = _("display name decorators")

    def __str__(self) -> str:
        return self.decorator
