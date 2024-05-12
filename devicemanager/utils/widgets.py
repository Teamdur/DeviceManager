from typing import NotRequired, TypedDict

from django import forms


class ActionLink(TypedDict):
    url: str
    name: str
    target: NotRequired[str]


class LinksWidget(forms.Widget):
    template_name = "widgets/links_widget.html"

    def __init__(self, action_links: list[ActionLink], *args, **kwargs):
        """
        urls_list= [{'url': '/admin/', name: 'admin panel'}]
        """
        self.action_links = action_links
        super(LinksWidget, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["action_links"] = self.action_links
        return context
