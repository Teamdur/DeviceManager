import pytest

from devicemanager.users.models import DisplayNameDecorator, User


@pytest.mark.django_db
def test_create_user():
    assert User.objects.count() == 0
    user = User.objects.create()
    assert User.objects.count() == 1

    assert user.name_decoration is None


@pytest.mark.django_db
def test_get_display_name():
    user = User.objects.create(
        username="test",
    )
    assert user.get_display_name() == "test"

    user.first_name = "John"
    assert user.get_display_name() == "John"

    user.last_name = "Doe"
    assert user.get_display_name() == "John Doe"

    user.name_decoration = DisplayNameDecorator.objects.create(decorator="Dr.")

    assert user.get_display_name() == "Dr. John Doe"
