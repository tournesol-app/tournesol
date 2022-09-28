"""
Administration interface of the `faq` app.
"""

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from faq.models import FAQAnswerLocale, FAQEntry, FAQuestionLocale


class HasAnswerListFilter(admin.SimpleListFilter):
    title = _("has answer?")
    parameter_name = "has_answer"

    def lookups(self, request, model_admin):
        return (
            (1, _("Yes")),
            (0, _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(
                answers__isnull=False,
            )
        if self.value() == "0":
            return queryset.filter(
                answers__isnull=True,
            )
        return queryset


class FAQuestionLocaleInline(admin.TabularInline):
    model = FAQuestionLocale
    extra = 0


class FAQAnswerLocaleInline(admin.TabularInline):
    model = FAQAnswerLocale
    extra = 0


@admin.register(FAQEntry)
class FAQEntryAdmin(admin.ModelAdmin):
    actions = ["enable_entries", "disable_entries"]
    search_fields = ("name",)
    list_display = ("name", "rank", "enabled", "has_answer")
    list_filter = (HasAnswerListFilter, "enabled")
    ordering = ("rank",)
    inlines = (FAQuestionLocaleInline, FAQAnswerLocaleInline)

    def get_queryset(self, request):
        qst = super().get_queryset(request)
        qst = qst.prefetch_related("answers")
        return qst

    @admin.display(description="has answer?", boolean=True)
    def has_answer(self, obj) -> bool:
        try:
            obj.answers
        except FAQEntry.answers.RelatedObjectDoesNotExist:  # pylint: disable=no-member
            return False
        else:
            return True

    @admin.action(description=_("Enable the selected entries."))
    def enable_entries(self, request, queryset):
        updated = queryset.update(enabled=True)
        self.message_user(
            request,
            ngettext_lazy(
                "%d entry was successfully marked as enabled.",
                "%d entries were successfully marked as enabled.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description=_("Disable the selected entries."))
    def disable_entries(self, request, queryset):
        updated = queryset.update(enabled=False)
        self.message_user(
            request,
            ngettext_lazy(
                "%d entry was successfully marked as disabled.",
                "%d entries were successfully marked as disabled.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )
