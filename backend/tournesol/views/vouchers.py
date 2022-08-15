"""
API endpoint to manipulate vouchers
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics

from tournesol.serializers.voucher import GivenVoucherSerializer, ReceivedVoucherSerializer
from vouch.models import Voucher


@extend_schema_view(
    post=extend_schema(
        description="Add a new voucher to a given username by the logged in user.",
    ),
)
class VoucherCreateView(generics.CreateAPIView):
    serializer_class = GivenVoucherSerializer


@extend_schema_view(
    delete=extend_schema(
        description="Delete a voucher given by the logged in user.",
    ),
)
class VoucherDestroyView(generics.DestroyAPIView):
    def get_queryset(self):
        return Voucher.objects.filter(by=self.request.user)


@extend_schema_view(
    get=extend_schema(
        description="List all the vouchers the logged in user has given.",
    ),
)
class VoucherGivenListView(generics.ListAPIView):
    serializer_class = GivenVoucherSerializer
    pagination_class = None

    def get_queryset(self):
        return Voucher.objects.filter(
            by=self.request.user,
        )


@extend_schema_view(
    get=extend_schema(
        description="List all the vouchers the logged in user has received.",
    ),
)
class VoucherReceivedListView(generics.ListAPIView):
    serializer_class = ReceivedVoucherSerializer
    pagination_class = None

    def get_queryset(self):
        return Voucher.objects.filter(
            to=self.request.user,
        )
