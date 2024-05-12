import typing
from typing import Literal

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest
from jazzmin.settings import DARK_THEMES as JAZZMIN_DARK_THEMES
from jazzmin.settings import THEMES

from devicemanager.users.models import User

DARK_THEMES = tuple(JAZZMIN_DARK_THEMES)
LIGHT_THEMES = tuple(x for x in THEMES.keys() if x not in DARK_THEMES)


class UserPreferences:
    SESSION_KEY = "user_preferences"

    @typing.overload
    def __init__(self, request: HttpRequest, session: Literal[None], user: Literal[None]) -> None: ...

    @typing.overload
    def __init__(self, request: Literal[None], session: SessionBase, user: User | AnonymousUser) -> None: ...

    def __init__(
        self, request: HttpRequest = None, session: SessionBase = None, user: User | AnonymousUser = None
    ) -> None:
        if request is not None:
            self.session = request.session
            self.user = request.user
        else:
            self.session = session
            self.user = user
        self.preferences = {}
        if self.user is None or self.session is None:
            raise ValueError("Either request or user and session must be provided")
        self.refresh()

    def _load_from_db(self) -> dict:
        if self.user.is_anonymous:
            raise Exception("Anonymous user has no preferences stored in the database")
        return self.user.user_preferences

    def _load_from_session(self) -> dict:
        return self.session.get(self.SESSION_KEY, {})

    def refresh(self) -> None:
        if self.user.is_anonymous:
            self.preferences = self._load_from_session()
            return
        self.preferences = self._load_from_db()

    def _save_db(self) -> None:
        self.user.user_preferences = self.preferences
        self.user.save(update_fields=["user_preferences"])

    def _save_session(self) -> None:
        self.session[self.SESSION_KEY] = self.preferences
        self.session.save()

    def save(self) -> None:
        if self.user.is_anonymous:
            self._save_session()
            return
        self._save_db()

    def sync_session_to_db(self):
        if self.user.is_anonymous:
            return
        self.user.user_preferences = self._load_from_session()
        self.user.save(update_fields=["user_preferences"])
        self.session.pop(self.SESSION_KEY, None)
        self.session.save()

    @property
    def theme(self) -> str | None:
        return self.preferences.get("theme")

    @theme.setter
    def theme(self, value: str) -> None:
        self.preferences["theme"] = value
