"""
API returning preview images of entities.
"""
import numpy
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from PIL import Image

from tournesol.models import Entity
from tournesol.utils.cache import cache_page_no_i18n

from .default import (
    CACHE_ENTITY_PREVIEW,
    BasePreviewAPIView,
    draw_video_duration,
    get_preview_font_config,
    get_preview_frame,
)


class DynamicWebsitePreviewEntity(BasePreviewAPIView):
    """
    Return a preview of an entity, with its Tournesol score, comparisons and
    contributors.
    """

    permission_classes = []

    def _draw_logo(self, image: Image.Image, entity: Entity, upscale_ratio: int):
        """
        Draw the Tournesol logo on the provided image.

        If the Tournesol score of the entity is negative, nothing is drawn.
        """
        # Negative scores are displayed without the Tournesol logo, to have
        # more space to display the minus symbol, and to make it clear that
        # the entity is not currently trusted by Tournesol.
        poll_rating = entity.single_poll_rating

        # If the score has not been computed yet, display a centered flower.
        if poll_rating is None or poll_rating.tournesol_score is None:
            image.alpha_composite(
                self.get_ts_logo(tuple(numpy.multiply((34, 34), upscale_ratio))),
                dest=tuple(numpy.multiply((43, 24), upscale_ratio)),
            )

        elif not poll_rating.is_recommendation_unsafe:
            image.alpha_composite(
                self.get_ts_logo(tuple(numpy.multiply((34, 34), upscale_ratio))),
                dest=tuple(numpy.multiply((16, 24), upscale_ratio)),
            )

    @method_decorator(cache_page_no_i18n(CACHE_ENTITY_PREVIEW))
    @extend_schema(
        description="Generic preview of an entity.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, uid):
        try:
            entity = self.get_entity(uid)
        except Entity.DoesNotExist:
            return self.default_preview()

        if not self.is_video(entity):
            return self.default_preview()

        upscale_ratio = 2
        fnt_config = get_preview_font_config(upscale_ratio=upscale_ratio)
        preview_image = get_preview_frame(
            entity, fnt_config, upscale_ratio=upscale_ratio
        )

        try:
            youtube_thumbnail = self.get_best_quality_yt_thumbnail(entity)
        except ConnectionError:
            return self.default_preview()

        # (width, height, left, top)
        youtube_thumbnail_bbox = tuple(numpy.multiply((320, 180, 120, 0), upscale_ratio))

        if youtube_thumbnail is not None:
            youtube_thumbnail = youtube_thumbnail.resize(youtube_thumbnail_bbox[0:2])
            preview_image.paste(
                youtube_thumbnail, box=tuple(youtube_thumbnail_bbox[2:4])
            )

        draw_video_duration(preview_image, entity, youtube_thumbnail_bbox, upscale_ratio)
        self._draw_logo(preview_image, entity, upscale_ratio=upscale_ratio)

        response = HttpResponse(content_type="image/jpeg")
        preview_image.convert("RGB").save(response, "jpeg")
        return response
