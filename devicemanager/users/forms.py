import itertools

from django import forms

from devicemanager.users.user_preferences import DARK_THEMES, LIGHT_THEMES

THEME_CHOICES = tuple(
    (theme_name, theme_name.replace("_", " ").capitalize()) for theme_name in itertools.chain(DARK_THEMES, LIGHT_THEMES)
)


class ColorThemeChangeForm(forms.Form):
    theme = forms.ChoiceField(choices=THEME_CHOICES)
