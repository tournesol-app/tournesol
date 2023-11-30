"""
API returning default preview images of the Tournesol website.

Mainly used to provide URLs that can be used by the Open Graph protocol.
"""
import logging
from io import BytesIO
from typing import Optional

import numpy
import requests
from django.conf import settings
from django.http import FileResponse
from django.utils.decorators import method_decorator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from PIL import Image, ImageDraw, ImageFont
from requests.exceptions import Timeout
from rest_framework.views import APIView

from tournesol.entities.video import TYPE_VIDEO
from tournesol.models import Entity
from tournesol.models.poll import DEFAULT_POLL_NAME
from tournesol.renderers import ImageRenderer
from tournesol.utils.cache import cache_page_no_i18n
from tournesol.utils.constants import REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

BASE_DIR = settings.BASE_DIR

CACHE_DEFAULT_PREVIEW = 3600 * 24  # 24h
CACHE_ENTITY_PREVIEW = 3600 * 2

FOOTER_FONT_LOCATION = "tournesol/resources/Poppins-Medium.ttf"
LIGHT_FONT_LOCATION = "tournesol/resources/Poppins-Light.ttf"
LIGHT_ITALIC_FONT_LOCATION = "tournesol/resources/Poppins-LightItalic.ttf"
REGULAR_FONT_LOCATION = "tournesol/resources/Poppins-Regular.ttf"
DURATION_FONT_LOCATION = "tournesol/resources/Roboto-Bold.ttf"
ENTITY_N_CONTRIBUTORS_XY = (60, 98)
ENTITY_TITLE_XY = (128, 194)

TOURNESOL_SCORE_XY = (84, 30)
TOURNESOL_SCORE_UNSAFE_XY = (60, 30)

COLOR_YELLOW_BORDER = (255, 200, 0, 255)
COLOR_YELLOW_BACKGROUND = (255, 200, 0, 16)
COLOR_WHITE_BACKGROUND = (255, 250, 230, 255)
COLOR_BROWN_FONT = (29, 26, 20, 255)
COLOR_WHITE_FONT = (255, 255, 255, 255)
COLOR_GREY_FONT = (160, 155, 135, 255)
COLOR_UNSAFE_SCORE = (128, 128, 128, 248)
COLOR_DURATION_RECTANGLE = (0, 0, 0, 201)

YT_THUMBNAIL_MQ_SIZE = (320, 180)


class BasePreviewAPIView(APIView):
    """
    A generic mixin that provides common behaviours that can be used by all
    dynamic preview `APIView`.
    """

    renderer_classes = [ImageRenderer]

    def default_preview(self):
        # The file needs to remain open to be streamed and will be closed automatically
        # by FileResponse. A context-manager should not be used here.
        # pylint: disable=consider-using-with
        default_preview = open(
            str(BASE_DIR / "tournesol/resources/tournesol_screenshot_og.png"), "rb"
        )
        return FileResponse(default_preview, content_type="image/png")

    def get_entity(self, uid: str) -> Entity:
        try:
            entity = Entity.objects.with_prefetched_poll_ratings(poll_name=DEFAULT_POLL_NAME).get(
                uid=uid
            )
        except Entity.DoesNotExist as exc:
            logger.error("Preview impossible for entity with UID %s.", uid)
            logger.error("Exception caught: %s", exc)
            raise exc
        return entity

    def is_video(self, entity: Entity) -> bool:
        if entity.type != TYPE_VIDEO:
            logger.info("Preview not implemented for entity with UID %s.", entity.uid)
            return False
        return True

    def get_ts_logo(self, size: tuple):
        return (
            Image.open(BASE_DIR / "tournesol/resources/Logo64.png")
            .convert("RGBA")
            .resize(size)
        )

    def get_yt_thumbnail(
        self, entity: Entity, quality="mq", return_none_on_404=False
    ) -> Optional[Image.Image]:
        # Quality can be: hq, mq, sd, or maxres (https://stackoverflow.com/a/34784842/188760)
        url = f"https://img.youtube.com/vi/{entity.video_id}/{quality}default.jpg"
        try:
            thumbnail_response = requests.get(url, timeout=REQUEST_TIMEOUT)
        except (ConnectionError, Timeout) as exc:
            logger.error("Preview failed for entity with UID %s.", entity.uid)
            logger.error("Exception caught: %s", exc)
            raise exc

        if thumbnail_response.status_code == 404 and return_none_on_404:
            return None

        if thumbnail_response.status_code != 200:
            # We chose to not raise an error here because the responses often
            # have a non-200 status while containing the right content (e.g.
            # 304, 443).
            # raise ConnectionError
            logger.warning(
                "Fetching YouTube thumbnail has non-200 status: %s",
                thumbnail_response.status_code,
            )

        return Image.open(BytesIO(thumbnail_response.content)).convert("RGBA")

    def get_best_quality_yt_thumbnail(self, entity: Entity) -> Optional[Image.Image]:
        result = self.get_yt_thumbnail(
            entity, quality="maxres", return_none_on_404=True
        )
        if result is not None:
            return result

        result = self.get_yt_thumbnail(entity, quality="hq", return_none_on_404=True)
        if result is not None:
            # HQ quality returns an image of 480x360 with black borders above and below
            # the thumbnail so we crop the black borders to return the same aspect ratio as
            # "maxres" and "mq" qualities
            result = result.crop((0, 45, 479, 359 - 45))
            return result

        result = self.get_yt_thumbnail(entity, quality="mq")

        # If the thumbnail doesn't exist a placeholder is returned with a different aspect ratio.
        # We always crop to make sure we always return the expected aspect ratio (16:9).
        if result is not None:
            width, height = result.size
            border_height = int((height - width * 9 / 16) // 2)
            result = result.crop((0, border_height, width - 1, height - 1 - border_height))
        return result


def get_preview_font_config(upscale_ratio=1) -> dict:
    config = {
        "ts_score": ImageFont.truetype(
            str(BASE_DIR / FOOTER_FONT_LOCATION), 32 * upscale_ratio
        ),
        "entity_title": ImageFont.truetype(
            str(BASE_DIR / FOOTER_FONT_LOCATION), 14 * upscale_ratio
        ),
        "entity_uploader": ImageFont.truetype(
            str(BASE_DIR / FOOTER_FONT_LOCATION), 11 * upscale_ratio
        ),
        "entity_ratings": ImageFont.truetype(
            str(BASE_DIR / FOOTER_FONT_LOCATION), 22 * upscale_ratio
        ),
        "entity_ratings_label": ImageFont.truetype(
            str(BASE_DIR / FOOTER_FONT_LOCATION), 14 * upscale_ratio
        ),
        "recommendations_headline": ImageFont.truetype(
            str(BASE_DIR / REGULAR_FONT_LOCATION), 14 * upscale_ratio
        ),
        "recommendations_title": ImageFont.truetype(
            str(BASE_DIR / LIGHT_FONT_LOCATION), 11 * upscale_ratio
        ),
        "recommendations_rating": ImageFont.truetype(
            str(BASE_DIR / LIGHT_ITALIC_FONT_LOCATION), 10 * upscale_ratio
        ),
        "recommendations_metadata": ImageFont.truetype(
            str(BASE_DIR / LIGHT_FONT_LOCATION), 9 * upscale_ratio
        ),
        "recommendations_ts_score": ImageFont.truetype(
            str(BASE_DIR / REGULAR_FONT_LOCATION), 16 * upscale_ratio
        ),
        "faq_headline": ImageFont.truetype(
            str(BASE_DIR / REGULAR_FONT_LOCATION), 14 * upscale_ratio
        ),
        "faq_question": ImageFont.truetype(
            str(BASE_DIR / REGULAR_FONT_LOCATION), 21 * upscale_ratio
        ),
    }
    return config


def truncate_text(draw, text, font, available_width):
    if draw.textlength(text, font=font) <= available_width:
        return text

    # Dichotomic search
    ellipsis = "…"
    left = 1
    right = len(text)

    while right - left > 1:
        middle = (left + right) // 2
        truncated = text[:middle] + ellipsis
        width = draw.textlength(truncated, font=font)
        if width <= available_width:
            left = middle
        else:
            right = middle

    truncated = text[:left] + ellipsis
    return truncated


def font_height(font):
    ascent, descent = font.getmetrics()
    return ascent + descent


def get_preview_frame(entity: Entity, fnt_config, upscale_ratio=1) -> Image.Image:
    tournesol_frame = Image.new(
        "RGBA", (440 * upscale_ratio, 240 * upscale_ratio), COLOR_WHITE_BACKGROUND
    )
    tournesol_frame_draw = ImageDraw.Draw(tournesol_frame)

    full_title = entity.metadata.get("name", "")
    truncated_title = truncate_text(
        tournesol_frame_draw,
        full_title,
        font=fnt_config["entity_title"],
        available_width=300 * upscale_ratio,
    )

    full_uploader = entity.metadata.get("uploader", "")
    truncated_uploader = truncate_text(
        tournesol_frame_draw,
        full_uploader,
        font=fnt_config["entity_title"],
        available_width=300 * upscale_ratio,
    )

    tournesol_frame_draw.text(
        tuple(numpy.multiply((ENTITY_TITLE_XY), upscale_ratio)),
        truncated_uploader,
        font=fnt_config["entity_uploader"],
        fill=COLOR_BROWN_FONT,
    )
    tournesol_frame_draw.text(
        tuple(numpy.multiply((ENTITY_TITLE_XY[0], ENTITY_TITLE_XY[1] + 18), upscale_ratio)),
        truncated_title,
        font=fnt_config["entity_title"],
        fill=COLOR_BROWN_FONT,
    )

    poll_rating = entity.single_poll_rating
    if poll_rating is not None and poll_rating.tournesol_score is not None:
        score = poll_rating.tournesol_score

        if poll_rating.is_recommendation_unsafe:
            score_color = COLOR_UNSAFE_SCORE
            score_xy = TOURNESOL_SCORE_UNSAFE_XY
        else:
            score_xy = TOURNESOL_SCORE_XY
            score_color = COLOR_BROWN_FONT

        tournesol_frame_draw.text(
            tuple(numpy.multiply(score_xy, upscale_ratio)),
            f"{score:.0f}",
            font=fnt_config["ts_score"],
            fill=score_color,
            anchor="mt",
        )
    x_coordinate, y_coordinate = ENTITY_N_CONTRIBUTORS_XY
    tournesol_frame_draw.text(
        tuple(numpy.multiply((x_coordinate, y_coordinate), upscale_ratio)),
        f"{poll_rating.n_comparisons if poll_rating else 0}",
        font=fnt_config["entity_ratings"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.text(
        tuple(numpy.multiply((x_coordinate, y_coordinate + 26), upscale_ratio)),
        "comparisons",
        font=fnt_config["entity_ratings_label"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.text(
        tuple(numpy.multiply((x_coordinate, y_coordinate + 82), upscale_ratio)),
        f"{poll_rating.n_contributors if poll_rating else 0}",
        font=fnt_config["entity_ratings"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.text(
        tuple(numpy.multiply((x_coordinate, y_coordinate + 108), upscale_ratio)),
        "contributors",
        font=fnt_config["entity_ratings_label"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.rectangle(
        (
            tuple(numpy.multiply((114, 0), upscale_ratio)),
            tuple(numpy.multiply((120, 240), upscale_ratio)),
        ),
        fill=COLOR_YELLOW_BORDER,
    )
    tournesol_frame_draw.rectangle(
        (
            tuple(numpy.multiply((120, 180), upscale_ratio)),
            tuple(numpy.multiply((440, 186), upscale_ratio)),
        ),
        fill=COLOR_YELLOW_BORDER,
    )
    return tournesol_frame


def draw_video_duration(image: Image.Image, entity: Entity, thumbnail_bbox, upscale_ratio: int):
    # pylint: disable=too-many-locals
    """
    Draw the duration of a video `entity` on the provided `image`.

    The position is determined according to the `thumbnail_bbox`, so that it
    is displayed in the bottom right corner of the thumbnail.
    """
    font_size = 14 * upscale_ratio
    font = ImageFont.truetype(str(BASE_DIR / DURATION_FONT_LOCATION), font_size)

    duration = entity.metadata.get("duration")
    if not duration:
        return
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)

    # creating a PIL.Image to get a Draw context, image later resized to text length
    overlay = Image.new("RGBA", (1, 1), COLOR_DURATION_RECTANGLE)
    overlay_draw = ImageDraw.Draw(overlay)

    padding = tuple(numpy.multiply((5, 1), upscale_ratio))
    duration_formatted = f"{str(hours) + ':' if hours > 0 else ''}{minutes:02d}:{seconds:02d}"
    duration_text_size = (
        int(overlay_draw.textlength(duration_formatted, font=font)) + padding[0],
        font_size + padding[1],
    )

    overlay = overlay.resize(duration_text_size)
    # need to reinstanciate Draw after resizing, there must be a better way
    overlay_draw = ImageDraw.Draw(overlay)

    overlay_draw.text(
        (padding[0]//2, padding[1]//2),
        duration_formatted,
        font=font,
        fill=COLOR_WHITE_FONT
    )

    image.alpha_composite(
        overlay,
        dest=(
            # all values are already upscaled (if applicable)
            thumbnail_bbox[0] + thumbnail_bbox[2] - duration_text_size[0],
            thumbnail_bbox[1] + thumbnail_bbox[3] - duration_text_size[1],
        ),
    )


def get_headline(upscale_ratio: int):
    headline_height = 30
    border_width = 6
    headline = Image.new(
        "RGBA", (440 * upscale_ratio, headline_height * upscale_ratio), COLOR_WHITE_BACKGROUND
    )

    headline_border = Image.new(
        "RGBA", (440 * upscale_ratio, border_width * upscale_ratio), COLOR_YELLOW_BORDER
    )
    headline_border_position = (0, (headline_height - border_width) * upscale_ratio)

    headline.paste(headline_border, headline_border_position)

    return headline


class DynamicWebsitePreviewDefault(BasePreviewAPIView):
    """
    Return the default preview of the Tournesol front end.
    """

    permission_classes = []

    @method_decorator(cache_page_no_i18n(CACHE_DEFAULT_PREVIEW))
    @extend_schema(
        description="Default website preview.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        return self.default_preview()
