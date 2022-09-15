"""
Administration interface of the `vouch` app.
"""

from django.contrib import admin

from vouch.models import Voucher


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    search_fields = ("by__username", "to__username")
    list_display = (
        "by",
        "to",
        "value",
        "is_public",
    )
    list_filter = ("is_public",)

    def get_queryset(self, request):
        qst = super().get_queryset(request)
        qst = qst.select_related("by", "to")
        return qst
