"""
API returning preview images of entities.
"""

import logging

import numpy
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from PIL import Image, ImageDraw

from tournesol.models import Entity
from tournesol.utils.cache import cache_page_no_i18n

from .default import (
    CACHE_ENTITY_PREVIEW,
    COLOR_UNSAFE_SCORE,
    COLOR_YELLOW_FONT,
    PREVIEW_BASE_SIZE,
    BasePreviewAPIView,
    font_height,
    get_preview_font_config,
)

logger = logging.getLogger(__name__)


TS_SCORE_OVERLAY_COLOR = (58, 58, 58, 224)
TS_SCORE_OVERLAY_MARGIN_B = 0
TS_SCORE_OVERLAY_PADDING_X = 10

# Shift the score position to the left and to the top, to make space for the logo.
TS_SCORE_SHIFT_L = 8
TS_SCORE_SHIFT_T = 2

TS_LOGO_MARGIN = (2, 4)
TS_LOGO_SIZE = (19, 19)


class DynamicWebsitePreviewEntity(BasePreviewAPIView):
    """
    Return a preview of an entity, with its Tournesol score.
    """

    permission_classes = []

    @staticmethod
    def draw_score(  # pylint: disable=too-many-arguments
        *,
        image: Image.Image,
        score_overlay: Image.Image,
        score: float,
        color: tuple,
        shift_l: int,
        shift_t: int,
        margin_bottom: int,
        font_config,
    ):
        image_draw = ImageDraw.Draw(image)
        image_draw.text(
            (
                image.size[0] - (score_overlay.size[0] / 2) - shift_l,
                image.size[1] - (score_overlay.size[1] / 2) - shift_t - margin_bottom,
            ),
            f"{score:.0f}",
            font=font_config["entity_preview_ts_score"],
            fill=color,
            anchor="mm",
        )

    @staticmethod
    def draw_score_overlay(
        image: Image.Image, size: tuple[int, int], upscale_ratio: int
    ) -> tuple[Image.Image, int]:
        score_overlay = Image.new(mode="RGBA", size=tuple(numpy.multiply(size, upscale_ratio)))
        score_overlay_draw = ImageDraw.Draw(score_overlay)
        score_overlay_draw.rounded_rectangle(
            [(0, 0), tuple(numpy.multiply(size, upscale_ratio))],
            radius=14,
            fill=TS_SCORE_OVERLAY_COLOR,
            corners=[True, False, False, False],
        )

        score_overlay_margin_b = TS_SCORE_OVERLAY_MARGIN_B * upscale_ratio

        image.alpha_composite(
            im=score_overlay,
            dest=(
                image.size[0] - score_overlay.size[0],
                image.size[1] - score_overlay.size[1] - score_overlay_margin_b,
            ),
        )

        return score_overlay, score_overlay_margin_b

    def add_tournesol_score(
        self, image: Image.Image, entity: Entity, upscale_ratio: int, font_config
    ):
        """
        Draw the entity's Tournesol score on the provided image.

        Non-trusted entities (i.e. with an unsafe rating) are displayed
        without the Tournesol logo.
        """
        poll_rating = entity.single_poll_rating

        # If the score has not been computed yet, display nothing.
        if poll_rating is None or poll_rating.tournesol_score is None:
            return

        if poll_rating.is_recommendation_unsafe:
            score_color = COLOR_UNSAFE_SCORE
        else:
            score_color = COLOR_YELLOW_FONT

        shift_l = int(TS_SCORE_SHIFT_L / 2) * upscale_ratio
        shift_t = int(TS_SCORE_SHIFT_T / 2) * upscale_ratio

        score_overlay_size = (
            max(
                int(
                    font_config["entity_preview_ts_score"].getlength(
                        str(int(poll_rating.tournesol_score))
                    )
                    / upscale_ratio
                )
                + TS_SCORE_SHIFT_L
                + TS_SCORE_OVERLAY_PADDING_X,
                60,
            ),
            int(font_height(font_config["entity_preview_ts_score"]) / upscale_ratio),
        )

        score_overlay, score_overlay_margin_b = DynamicWebsitePreviewEntity.draw_score_overlay(
            image=image, size=score_overlay_size, upscale_ratio=upscale_ratio
        )
        DynamicWebsitePreviewEntity.draw_score(
            image=image,
            score_overlay=score_overlay,
            score=poll_rating.tournesol_score,
            color=score_color,
            shift_l=shift_l,
            shift_t=shift_t,
            margin_bottom=score_overlay_margin_b,
            font_config=font_config,
        )

        if poll_rating.is_recommendation_unsafe:
            logo = (
                self.get_ts_logo(tuple(numpy.multiply(TS_LOGO_SIZE, upscale_ratio)))
                .convert("LA")
                .convert("RGBA")
            )
        else:
            logo = self.get_ts_logo(tuple(numpy.multiply(TS_LOGO_SIZE, upscale_ratio)))

        image.alpha_composite(
            logo,
            dest=(
                image.size[0]
                - TS_LOGO_SIZE[0] * upscale_ratio
                - TS_LOGO_MARGIN[0] * upscale_ratio,
                image.size[1]
                - TS_LOGO_SIZE[1] * upscale_ratio
                - TS_LOGO_MARGIN[1] * upscale_ratio
                - score_overlay_margin_b,
            ),
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
        font_config = get_preview_font_config(upscale_ratio=upscale_ratio)
        preview_image = Image.new("RGBA", tuple(numpy.multiply(PREVIEW_BASE_SIZE, upscale_ratio)))

        try:
            youtube_thumbnail = self.get_best_quality_yt_thumbnail(entity)
        except Exception as exc:   # pylint: disable=broad-except
            logger.info("Fallback to default preview, after exception: %s", exc)
            return self.default_preview()

        if youtube_thumbnail is not None:
            youtube_thumbnail = youtube_thumbnail.resize(preview_image.size)
            preview_image.paste(youtube_thumbnail, box=(0, 0))

        self.add_tournesol_score(
            preview_image, entity, upscale_ratio=upscale_ratio, font_config=font_config
        )

        response = HttpResponse(content_type="image/jpeg")
        preview_image.convert("RGB").save(response, "jpeg")
        return response
