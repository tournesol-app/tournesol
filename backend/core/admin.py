"""
Administration interface of `core` app.
"""

from typing import List, Tuple

from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Count, Func, OuterRef, Subquery
from django.db.models.query import QuerySet

from .models import Degree, EmailDomain, Expertise, ExpertiseKeyword, User, VerifiableEmail


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    pass


class IsTrustedFilter(admin.SimpleListFilter):
    title = "is trusted"
    parameter_name = "is_trusted"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("1", "Yes"),
            ("0", "No"),
        )

    def queryset(self, request, queryset: QuerySet[User]):
        if self.value() == "1":
            return queryset.filter(pk__in=User.trusted_users())
        if self.value() == "0":
            return queryset.exclude(pk__in=User.trusted_users())


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-date_joined"]
    list_filter = DjangoUserAdmin.list_filter + (IsTrustedFilter,)
    list_display = (
        "username",
        "email",
        "is_trusted",
        "is_active",
        "get_n_comparisons",
        "date_joined",
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    @staticmethod
    @admin.display(description="# comparisons", ordering="n_comparisons")
    def get_n_comparisons(user):
        return user.n_comparisons

    def get_queryset(self, request):
        """
        Return a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = super().get_queryset(request)
        return qs.annotate(n_comparisons=Count("comparisons"))

    def get_fieldsets(self, request, obj) -> List[Tuple]:
        fieldsets = super().get_fieldsets(request, obj=obj)
        if not obj:
            return fieldsets

        # For existing user, show all fields from our custom User model that
        # are not already present on the page, in a separate fieldsets.
        existing_fields = set(flatten_fieldsets(fieldsets))
        return fieldsets + (
            (
                "Other fields",
                {
                    "classes": ("collapse",),
                    "fields": tuple(
                        f.name
                        for f in User._meta.local_fields
                        if f.name != "id" and f.name not in existing_fields
                    ),
                },
            ),
        )

    @admin.display(boolean=True)
    def is_trusted(self, instance):
        return instance.is_trusted


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    pass


@admin.register(ExpertiseKeyword)
class ExpertiseKeywordAdmin(admin.ModelAdmin):
    pass


@admin.action(description="Mark selected domains as accepted")
def make_accepted(modeladmin, request, queryset):
    queryset.update(status=EmailDomain.STATUS_ACCEPTED)


@admin.action(description="Mark selected domains as rejected")
def make_rejected(modeladmin, request, queryset):
    queryset.update(status=EmailDomain.STATUS_REJECTED)


@admin.register(EmailDomain)
class EmailDomainAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "status",
        "user_number",
    )
    list_editable = ("status",)
    list_filter = ("status",)
    actions = [make_accepted, make_rejected]
    radio_fields = {"status": admin.HORIZONTAL}
    search_fields = ["domain"]

    def get_queryset(self, request):
        qst = super().get_queryset(request)
        qst = qst.annotate(
            _user_number=Subquery(
                User.objects.filter(email__iendswith=OuterRef("domain"))
                .annotate(count=Func("id", function="Count"))
                .values("count")
            )
        )
        return qst

    @admin.display(ordering="-_user_number", description="# users")
    def user_number(self, obj):
        return obj._user_number


@admin.register(VerifiableEmail)
class VerifiableEmailAdmin(admin.ModelAdmin):
    pass
