from allauth.socialaccount.models import SocialApp, SocialToken
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from devicemanager.users.models import DisplayNameDecorator, User

admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    readonly_fields = ("name", "date_joined", "last_login")
    list_display = (
        "name",
        "username",
        "name_decoration",
        "email",
        "first_name",
        "last_name",
        "is_staff",
    )

    def get_fieldsets(self, request, obj: User | None = None):
        if not obj:
            return self.add_fieldsets

        fieldsets = (
            (None, {"fields": ["username", "password"]}),
            (
                _("Personal info"),
                {"fields": ["name_decoration", "first_name", "last_name", "email"]},
            ),
            (
                _("Permissions"),
                {
                    "fields": [
                        "is_active",
                        "is_staff",
                        "is_superuser",
                        "groups",
                        "user_permissions",
                    ],
                },
            ),
            (_("Important dates"), {"fields": ["last_login", "date_joined"]}),
        )

        if obj.first_name and obj.last_name:
            fieldsets[0][1]["fields"] = ["name", "username", "password"]

        return fieldsets

    @admin.display(description=_("Name"))
    def name(self, obj: User):
        return obj.get_display_name() or obj.username

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                "is_superuser",
                "username",
            }

        # Prevent non-superusers from editing their own permissions
        if not is_superuser and obj is not None and obj == request.user:
            disabled_fields |= {
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            }

        for field in disabled_fields:
            try:
                form.base_fields[field].disabled = True
            except KeyError:
                pass

        return form


@admin.register(DisplayNameDecorator)
class DisplayNameDecoratorAdmin(admin.ModelAdmin):
    list_display = ("decorator",)
    search_fields = ("decorator",)
