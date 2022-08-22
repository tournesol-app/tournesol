"""
The vouch app routes.
"""

from django.urls import path

from vouch.views import (
    VoucherCreateAPIView,
    VoucherDestroyAPIView,
    VoucherGivenListAPIView,
    VoucherReceivedListAPIView,
)

urlpatterns = [
    # Vouchers API
    path(
        "vouchers/given/",
        VoucherGivenListAPIView.as_view(),
        name="usersme_vouchers_given",
    ),
    path(
        "vouchers/received/",
        VoucherReceivedListAPIView.as_view(),
        name="usersme_vouchers_received",
    ),
    path(
        "vouchers/",
        VoucherCreateAPIView.as_view(),
        name="usersme_vouchers_create",
    ),
    path(
        "vouchers/<str:pk>/",
        VoucherDestroyAPIView.as_view(),
        name="usersme_vouchers_destroy",
    ),
]
