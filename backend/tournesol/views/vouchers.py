"""
API endpoint to manipulate vouchers
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from tournesol.serializers.voucher import VoucherSerializer
from vouch.models import Voucher


@extend_schema_view(
    create=extend_schema(
        description="Add a new voucher to a given username by the logged in user.",
    ),
)
class VouchersViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Voucher.objects.none()
    permission_classes = [IsAuthenticated]
    serializer_class = VoucherSerializer

    def get_queryset(self):
        return Voucher.objects.filter(by=self.request.user)
