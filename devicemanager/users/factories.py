import factory

from devicemanager.users.models import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    @factory.lazy_attribute
    def email(self):
        return f"{self.first_name.lower()}.{self.last_name.lower()}@example.com"
