from zoneinfo import ZoneInfo

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from backoffice.models import (
    Banner,
    BannerLocale,
    FAQAnswerLocale,
    FAQEntry,
    FAQuestionLocale,
    TalkEntry,
)


@admin.register(TalkEntry)
class TalkEntryAdmin(admin.ModelAdmin):
    search_fields = ("title", "speakers")
    ordering = ("-date",)
    list_display = (
        "get_human_time_europe_paris",
        "get_server_time",
        "event_type",
        "title",
        "get_youtube_link",
        "public",
    )
    list_display_links = ("get_human_time_europe_paris",)
    list_filter = ("event_type", "public",)

    @admin.display(description="Server time", ordering="date")
    def get_server_time(self, obj):
        return obj.date

    @admin.display(description="Time (Europe/Paris)", ordering="date")
    def get_human_time_europe_paris(self, obj):
        human_format = "%d of %B %Y %H:%M (%Z)"

        if not obj.date:
            return None

        return obj.date.astimezone(ZoneInfo("Europe/Paris")).strftime(human_format)

    @admin.display(description="YouTube link")
    def get_youtube_link(self, obj):
        return obj.html_youtube_link()


class BannerLocaleInline(admin.StackedInline):
    min_num = 1
    model = BannerLocale
    extra = 0


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    actions = ["enable_banners", "disable_banners"]
    search_field = ("name",)
    list_display = (
        "name",
        "date_start",
        "date_end",
        "priority",
        "security_advisory",
        "enabled",
    )
    list_filter = ("enabled", "security_advisory")
    inlines = (BannerLocaleInline,)

    @admin.action(description=_("Enable the selected banners."))
    def enable_banners(self, request, queryset):
        queryset.update(enabled=True)

    @admin.action(description=_("Disable the selected banners."))
    def disable_banners(self, request, queryset):
        queryset.update(enabled=False)


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
        if obj.answers.exists():
            return True
        return False

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
