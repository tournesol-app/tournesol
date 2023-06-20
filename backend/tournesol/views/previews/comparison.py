"""
API returning preview images of the Tournesol's FAQ entries.
"""
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.views import APIView

from tournesol.models import Entity
from tournesol.utils.cache import cache_page_no_i18n

from ..preview import CACHE_ENTITY_PREVIEW, BasePreviewAPIView, ComparisonPreviewGenerator


class DynamicWebsitePreviewComparison(BasePreviewAPIView, APIView):
    """
    Return the preview of the Tournesol front end's comparison page.
    """

    permission_classes = []

    @method_decorator(cache_page_no_i18n(CACHE_ENTITY_PREVIEW))
    @extend_schema(
        description="Preview of the website comparison page.",
        responses={200: OpenApiTypes.BINARY},
        parameters=[
            OpenApiParameter(
                "uidA",
                OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
            OpenApiParameter(
                "uidB",
                OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
        ],
    )
    def get(self, request):
        uid_a = request.query_params.get("uidA")
        uid_b = request.query_params.get("uidB")

        if uid_a is None or uid_b is None:
            return self.default_preview()

        try:
            entity_a = self.get_entity(uid_a)
            entity_b = self.get_entity(uid_b)
        except Entity.DoesNotExist:
            return self.default_preview()

        if not self.is_video(entity_a) or not self.is_video(entity_b):
            return self.default_preview()

        try:
            thumbnail_a = self.get_best_quality_yt_thumbnail(entity_a)
            thumbnail_b = self.get_best_quality_yt_thumbnail(entity_b)
        except ConnectionError:
            return self.default_preview()

        generator = ComparisonPreviewGenerator()
        final = generator.render(entity_a, entity_b, thumbnail_a, thumbnail_b)

        response = HttpResponse(content_type="image/jpeg")
        final.convert("RGB").save(response, "jpeg")
        return response
