"""
API returning preview images of entities.
"""

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
    BasePreviewAPIView,
    draw_video_duration,
    get_preview_font_config,
    get_preview_frame,
    PREVIEW_BASE_SIZE,
    COLOR_YELLOW_FONT,
    COLOR_UNSAFE_SCORE,
)

TS_SCORE_OVERLAY_COLOR = (58, 58, 58, 224)
TS_SCORE_OVERLAY_MARGIN_B = 0
TS_SCORE_OVERLAY_PADDING_R = 8
TS_SCORE_OVERLAY_PADDING_B = 4
TS_SCORE_OVERLAY_SIZE = (48 + TS_SCORE_OVERLAY_PADDING_R, 34 + TS_SCORE_OVERLAY_PADDING_B)

TS_LOGO_MARGIN = (2, 4)


class DynamicWebsitePreviewEntity(BasePreviewAPIView):
    """
    Return a preview of an entity, with its Tournesol score.
    """

    permission_classes = []

    @staticmethod
    def draw_score(
        score: float,
        image: Image.Image,
        score_overlay: Image.Image,
        padding_r: int,
        padding_b: int,
        margin_bottom: int,
        color,
        font_config,
    ):
        image_draw = ImageDraw.Draw(image)
        image_draw.text(
            (
                image.size[0] - (score_overlay.size[0] / 2) - padding_r,
                image.size[1] - (score_overlay.size[1] / 2) - padding_b - margin_bottom,
            ),
            f"{score:.0f}",
            font=font_config["entity_preview_ts_score"],
            fill=color,
            anchor="mm",
        )

    @staticmethod
    def draw_score_overlay(image: Image.Image, upscale_ratio: int) -> tuple[Image.Image, int]:
        score_overlay = Image.new(
            mode="RGBA", size=tuple(numpy.multiply(TS_SCORE_OVERLAY_SIZE, upscale_ratio))
        )
        score_overlay_draw = ImageDraw.Draw(score_overlay)
        score_overlay_draw.rounded_rectangle(
            [(0, 0), tuple(numpy.multiply(TS_SCORE_OVERLAY_SIZE, upscale_ratio))],
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
            return

        if poll_rating.is_recommendation_unsafe:
            score_padding_r, score_padding_b = 0, 0
            score_color = COLOR_UNSAFE_SCORE
        else:
            score_padding_r = int(TS_SCORE_OVERLAY_PADDING_R / 2) * upscale_ratio
            score_padding_b = int(TS_SCORE_OVERLAY_PADDING_B / 2) * upscale_ratio
            score_color = COLOR_YELLOW_FONT

        score_overlay, score_overlay_margin_b = DynamicWebsitePreviewEntity.draw_score_overlay(
            image=image, upscale_ratio=upscale_ratio
        )
        DynamicWebsitePreviewEntity.draw_score(
            score=poll_rating.tournesol_score,
            image=image,
            score_overlay=score_overlay,
            padding_r=score_padding_r,
            padding_b=score_padding_b,
            margin_bottom=score_overlay_margin_b,
            font_config=font_config,
            color=score_color,
        )

        if not poll_rating.is_recommendation_unsafe:
            image.alpha_composite(
                self.get_ts_logo(tuple(numpy.multiply((16, 16), upscale_ratio))),
                dest=(
                    image.size[0] - 16 * upscale_ratio - TS_LOGO_MARGIN[0] * upscale_ratio,
                    image.size[1]
                    - 16 * upscale_ratio
                    - TS_LOGO_MARGIN[1] * upscale_ratio
                    - score_overlay_margin_b,
                ),
            )

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
        except ConnectionError:
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
