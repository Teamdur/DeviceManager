from django import forms
from django.utils.translation import gettext_lazy as _

from devicemanager.utils.widgets import ActionLink, LinksWidget


class FormActionItemsMixin(forms.Form):
    actions = forms.CharField(required=False, label=_("Actions"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["actions"].widget = LinksWidget(action_links=self.get_action_links())

    def get_action_links(self) -> list[ActionLink]:
        return []
