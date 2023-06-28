from zoneinfo import ZoneInfo

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from backoffice.banner.models import (
    Banner,
    BannerActionLabel,
    BannerActionLink,
    BannerText,
    BannerTitle,
)
from backoffice.talk.models import TalkEntry


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
    max_num = 1
    min_num = 1
    model = BannerTitle
    extra = 0


class BannerTextInline(admin.TabularInline):
    max_num = 1
    min_num = 1
    model = BannerText
    extra = 0


class BannerActionLabelInline(admin.TabularInline):
    max_num = 1
    min_num = 0
    model = BannerActionLabel
    extra = 0


class BannerActionLinkInline(admin.TabularInline):
    max_num = 1
    min_num = 0
    model = BannerActionLink
    extra = 0


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    actions = ["enable_banners", "disable_banners"]
    search_field = ("name")
    ordering = ("-date_start", "-date_end")
    list_display = (
        "name",
        "date_start",
        "date_end",
        "security_advisory",
        "enabled",
    )
    list_filter = ("enabled", "security_advisory")
    inlines = (
        BannerTitleInline, BannerTextInline, BannerActionLabelInline, BannerActionLinkInline
        )

    @admin.display(description="Start Date", ordering="date_start")
    def get_date_start(self, obj):
        return obj.date_start

    @admin.display(description="End Date", ordering="date_end")
    def get_date_end(self, obj):
        return obj.date_end

    @admin.action(description=_("Enable the selected banners."))
    def enable_banners(self, request, queryset):
        queryset.update(enabled=True)

    @admin.action(description=_("Disable the selected banners."))
    def disable_banners(self, request, queryset):
        queryset.update(enabled=False)
