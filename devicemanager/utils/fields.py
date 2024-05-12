from django.db.models import JSONField

__all__ = ["DictJSONField", "ListJSONField"]


class DictJSONField(JSONField):
    empty_values = [{}]


class ListJSONField(JSONField):
    empty_values = [[]]
    _default_hint = ("list", "[]")
