"""
The `vouch` app routes.
"""

from django.urls import path

from vouch.views import (
    VoucherCreateAPIView,
    VoucherGivenDestroyAPIView,
    VoucherGivenListAPIView,
    VoucherReceivedListAPIView,
)

urlpatterns = [
    path(
        "vouchers/",
        VoucherCreateAPIView.as_view(),
        name="usersme_vouchers_create",
    ),
    path(
        "vouchers/given/",
        VoucherGivenListAPIView.as_view(),
        name="usersme_vouchers_given",
    ),
    path(
        "vouchers/given/<str:username>/",
        VoucherGivenDestroyAPIView.as_view(),
        name="usersme_vouchers_destroy_given",
    ),
    path(
        "vouchers/received/",
        VoucherReceivedListAPIView.as_view(),
        name="usersme_vouchers_received",
    ),
]
