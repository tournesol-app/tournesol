"""
Defines Admin interface for Tournesol's core app
"""

from typing import List, Tuple
from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import (
    User,
    UserPreference,
    Degree,
    Expertise,
    ExpertiseKeyword,
    EmailDomain,
    VerifiableEmail,
)


@admin.register(UserPreference)
class UserPreferencesAdmin(admin.ModelAdmin):
    pass


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ['-date_joined']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def get_fieldsets(self, request, obj) -> List[Tuple]:
        fieldsets = super().get_fieldsets(request, obj=obj)
        if not obj:
            return fieldsets

        # For existing user, show all fields from our custom User model that
        # are not already present on the page, in a separate fieldsets.
        existing_fields = set(flatten_fieldsets(fieldsets))
        return fieldsets + (
            ('Other fields', {
                'classes': ('collapse',),
                'fields': tuple(
                    f.name
                    for f in User._meta.local_fields
                    if f.name != 'id' and f.name not in existing_fields
                ),
            }),
        )


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    pass


@admin.register(ExpertiseKeyword)
class ExpertiseKeywordAdmin(admin.ModelAdmin):
    pass


@admin.action(description='Mark selected domains as accepted')
def make_accepted(modeladmin, request, queryset):
    queryset.update(status=EmailDomain.STATUS_ACCEPTED)


@admin.action(description='Mark selected domains as rejected')
def make_rejected(modeladmin, request, queryset):
    queryset.update(status=EmailDomain.STATUS_REJECTED)


@admin.register(EmailDomain)
class EmailDomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'status')
    list_editable = ('status',)
    list_filter = ('status',)
    actions = [make_accepted, make_rejected]
    radio_fields = {"status": admin.HORIZONTAL}
    search_fields = ['domain']


@admin.register(VerifiableEmail)
class VerifiableEmailAdmin(admin.ModelAdmin):
    pass
