"""
Administration interface of `core` app.
"""

from typing import List, Tuple
from urllib.parse import urlencode

from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Count
from django.db.models.expressions import RawSQL
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Degree, EmailDomain, Expertise, ExpertiseKeyword, User, VerifiableEmail


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    """Interface to manage degrees (feature not developed yet)"""


class IsTrustedFilter(admin.SimpleListFilter):
    """Filter for displaying only trusted or untrusted users"""

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
            return queryset.filter(pk__in=User.with_trusted_email())
        if self.value() == "0":
            return queryset.exclude(pk__in=User.with_trusted_email())

        return queryset


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Interface to manage general data about users."""

    ordering = ["-date_joined"]
    list_filter = DjangoUserAdmin.list_filter + (IsTrustedFilter,)
    list_display = (
        "username",
        "email",
        "is_active",
        "is_trusted",
        "get_n_comparisons",
        "get_trust_score",
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

    fieldsets = DjangoUserAdmin.fieldsets + (
        (_("Tournesol - trust"), {"fields": ("trust_score",)}),
        (_("Tournesol - preferences"), {"fields": ("settings",)}),
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

    def get_fieldsets(self, request, obj=None) -> List[Tuple]:
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

    @admin.display(ordering="-trust_score", description="Trust score")
    def get_trust_score(self, instance):
        if instance.trust_score is None:
            return ""
        return f"{instance.trust_score:.1%}"


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    """Interface to manage expertise (feature not developed yet)"""


@admin.register(ExpertiseKeyword)
class ExpertiseKeywordAdmin(admin.ModelAdmin):
    """Interface to manage expertise keywords (feature not developed yet)"""


@admin.action(description="Mark selected domains as accepted")
def make_accepted(modeladmin, request, queryset):  # pylint: disable=unused-argument
    queryset.update(status=EmailDomain.STATUS_ACCEPTED)


@admin.action(description="Mark selected domains as rejected")
def make_rejected(modeladmin, request, queryset):  # pylint: disable=unused-argument
    queryset.update(status=EmailDomain.STATUS_REJECTED)


@admin.register(EmailDomain)
class EmailDomainAdmin(admin.ModelAdmin):
    """Interface to manage domains and their trust status"""

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
            user_number=RawSQL(
                """
                WITH count_by_domain AS MATERIALIZED (
                    SELECT
                        regexp_replace("email", '(.*)(@.*$)', '\\2') AS user_domain,
                        count(*) AS user_count
                    FROM core_user
                    GROUP BY user_domain
                )
                SELECT COALESCE(
                    (SELECT user_count FROM count_by_domain WHERE user_domain = domain),
                    0
                )
                """,
                (),
            )
        )
        return qst

    @admin.display(ordering="-user_number", description="# users")
    def user_number(self, obj):
        return format_html(
            '<a href="{}">{} user(s)</a>',
            f'{reverse("admin:core_user_changelist")}?{urlencode({"q": obj.domain})}',
            obj.user_number,
        )


@admin.register(VerifiableEmail)
class VerifiableEmailAdmin(admin.ModelAdmin):
    """Interface to manage individual emails verified or waiting to be verified"""
