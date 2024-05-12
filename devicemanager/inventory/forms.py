from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from devicemanager.inventory.models import Device
from devicemanager.utils.forms import FormActionItemsMixin
from devicemanager.utils.widgets import ActionLink


class DeviceForm(forms.ModelForm, FormActionItemsMixin):
    class Meta:
        model = Device
        exclude = ("id",)

    def get_action_links(self) -> list[ActionLink]:
        if self.instance and self.instance.pk:
            return self.get_action_data()
        return []

    def get_action_data(self) -> list[ActionLink]:
        return [
            {
                "url": reverse("inventory:qr-generate") + f"?ids={self.instance.pk}",
                "name": _("Generate QR code"),
            }
        ]


class QRCodeGenerationConfigForm(forms.ModelForm):
    included_labels = forms.MultipleChoiceField(
        label=_("Included labels"),
        choices=Device.LABELS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Device
        exclude = ("id",)
