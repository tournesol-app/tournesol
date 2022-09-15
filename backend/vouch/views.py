"""
API of the `vouch` app.
"""
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics

from core.models import User
from vouch.models import Voucher
from vouch.serializers import GivenVoucherSerializer, ReadOnlyVoucherSerializer


@extend_schema_view(
    post=extend_schema(
        description="The logged-in user give a voucher to the target user.",
    ),
)
class VoucherCreateAPIView(generics.CreateAPIView):
    serializer_class = GivenVoucherSerializer


@extend_schema_view(
    delete=extend_schema(
        description="Delete a voucher given to a target user by the logged-in user.",
    ),
)
class VoucherGivenDestroyAPIView(generics.DestroyAPIView):
    def get_object(self):
        target = get_object_or_404(User, username=self.kwargs["username"])
        return get_object_or_404(Voucher, by=self.request.user, to=target)


@extend_schema_view(
    get=extend_schema(
        description="List all the vouchers given by the the logged-in user.",
    ),
)
class VoucherGivenListAPIView(generics.ListAPIView):
    serializer_class = GivenVoucherSerializer
    pagination_class = None

    def get_queryset(self):
        return Voucher.objects.filter(
            by=self.request.user,
        )


@extend_schema_view(
    get=extend_schema(
        description="List all the vouchers received by the logged-in user",
    ),
)
class VoucherReceivedListAPIView(generics.ListAPIView):
    serializer_class = ReadOnlyVoucherSerializer
    pagination_class = None

    def get_queryset(self):
        return Voucher.objects.filter(
            to=self.request.user,
        )
