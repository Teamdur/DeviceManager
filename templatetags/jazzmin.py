import copy
import logging

from django.conf import settings
from django.template import Context
from django.templatetags.static import static
from jazzmin.settings import DEFAULT_UI_TWEAKS, THEMES
from jazzmin.templatetags.jazzmin import register

from devicemanager.users.user_preferences import (
    DARK_THEMES,
    LIGHT_THEMES,
    UserPreferences,
)

logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def get_jazzmin_ui_tweaks(context: Context) -> dict:
    raw_tweaks = copy.deepcopy(DEFAULT_UI_TWEAKS)
    raw_tweaks.update(getattr(settings, "JAZZMIN_UI_TWEAKS", {}))
    tweaks = {x: y for x, y in raw_tweaks.items() if y not in (None, "", False)}

    if tweaks.get("layout_boxed"):
        tweaks.pop("navbar_fixed", None)
        tweaks.pop("footer_fixed", None)

    bool_map = {
        "navbar_small_text": "text-sm",
        "footer_small_text": "text-sm",
        "body_small_text": "text-sm",
        "brand_small_text": "text-sm",
        "sidebar_nav_small_text": "text-sm",
        "no_navbar_border": "border-bottom-0",
        "sidebar_disable_expand": "sidebar-no-expand",
        "sidebar_nav_child_indent": "nav-child-indent",
        "sidebar_nav_compact_style": "nav-compact",
        "sidebar_nav_legacy_style": "nav-legacy",
        "sidebar_nav_flat_style": "nav-flat",
        "layout_boxed": "layout-boxed",
        "sidebar_fixed": "layout-fixed",
        "navbar_fixed": "layout-navbar-fixed",
        "footer_fixed": "layout-footer-fixed",
        "actions_sticky_top": "sticky-top",
    }

    for key, value in bool_map.items():
        if key in tweaks:
            tweaks[key] = value

    def classes(*args: str) -> str:
        return " ".join([tweaks.get(arg, "") for arg in args]).strip()

    if (request := context.get("request")) is not None:
        saved_theme = UserPreferences(request=request).theme
        if saved_theme:
            tweaks["theme"] = saved_theme

    theme = tweaks["theme"]
    if theme not in THEMES:
        logger.warning("{} not found in {}, using default".format(theme, THEMES.keys()))
        theme = "default"

    dark_mode_theme = tweaks.get("dark_mode_theme", None)
    if dark_mode_theme and dark_mode_theme not in DARK_THEMES:
        logger.warning("{} is not a dark theme, using darkly".format(dark_mode_theme))
        dark_mode_theme = "darkly"

    theme_body_classes = " theme-{}".format(theme)
    theme_navbar_classes = f" navbar-{"dark" if theme in DARK_THEMES else "light"}"
    if theme in DARK_THEMES:
        theme_body_classes += " dark-mode"

    ret = {
        "raw": raw_tweaks,
        "theme": {"name": theme, "src": static(THEMES[theme])},
        "sidebar_classes": classes("sidebar", "sidebar_disable_expand"),
        "navbar_classes": classes("navbar", "no_navbar_border", "navbar_small_text") + theme_navbar_classes,
        "body_classes": classes(
            "accent", "body_small_text", "navbar_fixed", "footer_fixed", "sidebar_fixed", "layout_boxed"
        )
        + theme_body_classes,
        "actions_classes": classes("actions_sticky_top"),
        "sidebar_list_classes": classes(
            "sidebar_nav_small_text",
            "sidebar_nav_flat_style",
            "sidebar_nav_legacy_style",
            "sidebar_nav_child_indent",
            "sidebar_nav_compact_style",
        ),
        "brand_classes": classes("brand_small_text", "brand_colour"),
        "footer_classes": classes("footer_small_text"),
        "button_classes": tweaks["button_classes"],
        "extra": {
            "dark_themes": DARK_THEMES,
            "light_themes": LIGHT_THEMES,
            "active_theme": theme,
        },
    }

    if dark_mode_theme:
        ret["dark_mode_theme"] = {"name": dark_mode_theme, "src": static(THEMES[dark_mode_theme])}

    return ret
