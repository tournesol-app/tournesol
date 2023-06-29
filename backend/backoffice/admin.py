from zoneinfo import ZoneInfo

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from backoffice.models.banner import (
    Banner,
    BannerActionLabel,
    BannerActionLink,
    BannerText,
    BannerTitle,
)
from backoffice.models.talk import TalkEntry


@admin.register(TalkEntry)
class TalkEntryAdmin(admin.ModelAdmin):
    search_fields = ("title", "speakers")
    ordering = ("-date",)
    list_display = (
        "get_human_time_europe_paris",
        "get_server_time",
        "title",
        "get_youtube_link",
        "public",
    )
    list_display_links = ("get_human_time_europe_paris",)
    list_filter = ("public",)

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


class BannerTitleInline(admin.TabularInline):
    min_num = 1
    model = BannerTitle
    extra = 0


class BannerTextInline(admin.TabularInline):
    min_num = 1
    model = BannerText
    extra = 0


class BannerActionLabelInline(admin.TabularInline):
    min_num = 0
    model = BannerActionLabel
    extra = 0


class BannerActionLinkInline(admin.TabularInline):
    min_num = 0
    model = BannerActionLink
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
    inlines = (
        BannerTitleInline,
        BannerTextInline,
        BannerActionLabelInline,
        BannerActionLinkInline,
    )

    @admin.action(description=_("Enable the selected banners."))
    def enable_banners(self, request, queryset):
        queryset.update(enabled=True)

    @admin.action(description=_("Disable the selected banners."))
    def disable_banners(self, request, queryset):
        queryset.update(enabled=False)
