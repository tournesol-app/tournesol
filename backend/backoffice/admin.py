from zoneinfo import ZoneInfo

from django.contrib import admin

from backoffice.models import TalkEntry


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
        human_format = "%Y-%m-%d %H:%M"

        if not obj.date:
            return None

        return obj.date.astimezone(ZoneInfo("Europe/Paris")).strftime(human_format)

    @admin.display(description="YouTube link")
    def get_youtube_link(self, obj):
        return obj.html_youtube_link()
