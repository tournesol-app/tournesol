"""
API returning preview images of some Tournesol front end's page.

Mainly used to provide URLs that can be used by the Open Graph protocol.
"""

import logging
from io import BytesIO

import requests
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiTypes, extend_schema
from PIL import Image, ImageDraw, ImageFont
from requests.exceptions import Timeout
from rest_framework.views import APIView

from tournesol.entities.video import TYPE_VIDEO
from tournesol.models.entity import Entity
from tournesol.utils.cache import cache_page_no_i18n
from tournesol.utils.constants import REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

BASE_DIR = settings.BASE_DIR

FOOTER_FONT_LOCATION = "tournesol/resources/Poppins-Medium.ttf"
ENTITY_N_CONTRIBUTORS_XY = (60, 98)
ENTITY_TITLE_XY = (128, 190)

TOURNESOL_SCORE_XY = (84, 30)
TOURNESOL_SCORE_NEGATIVE_XY = (60, 30)

COLOR_YELLOW_BORDER = (255, 200, 0, 255)
COLOR_YELLOW_BACKGROUND = (255, 200, 0, 16)
COLOR_WHITE_BACKGROUND = (255, 250, 230, 255)
COLOR_BROWN_FONT = (29, 26, 20, 255)
COLOR_NEGATIVE_SCORE = (128, 128, 128, 248)

YT_THUMBNAIL_MQ_SIZE = (320, 180)


class BasePreviewAPIView(APIView):
    """
    A generic mixin that provides common behaviours that can be used by all
    dynamic preview `APIView`.
    """

    def default_preview(self):
        with open(
            str(BASE_DIR / "tournesol/resources/tournesol_screenshot_og.png"), "rb"
        ) as default_preview:
            response = FileResponse(default_preview, content_type="image/png")
        return response

    def get_entity(self, uid: str) -> Entity:
        try:
            entity = Entity.objects.get(uid=uid)
        except Entity.DoesNotExist as exc:
            logger.error("Preview impossible for entity with UID %s.", uid)
            logger.error("Exception caught: %s", exc)
            raise exc
        return entity

    def is_video(self, entity: Entity) -> None:
        if entity.type != TYPE_VIDEO:
            logger.info("Preview not implemented for entity with UID %s.", entity.uid)
            return False
        return True

    def get_ts_logo(self, length: int):
        return (
            Image.open(BASE_DIR / "tournesol/resources/Logo64.png")
            .convert("RGBA")
            .resize((length, length))
        )

    def get_yt_thumbnail(self, entity: Entity) -> Image:
        url = f"https://img.youtube.com/vi/{entity.video_id}/mqdefault.jpg"
        try:
            thumbnail_response = requests.get(url, timeout=REQUEST_TIMEOUT)
        except (ConnectionError, Timeout) as exc:
            logger.error("Preview failed for entity with UID %s.", entity.uid)
            logger.error("Exception caught: %s", exc)
            raise exc

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


def get_preview_font_config() -> dict:
    config = {
        "ts_score": ImageFont.truetype(str(BASE_DIR / FOOTER_FONT_LOCATION), 32),
        "entity_title": ImageFont.truetype(str(BASE_DIR / FOOTER_FONT_LOCATION), 14),
        "entity_uploader": ImageFont.truetype(str(BASE_DIR / FOOTER_FONT_LOCATION), 13),
        "entity_ratings": ImageFont.truetype(str(BASE_DIR / FOOTER_FONT_LOCATION), 22),
        "entity_ratings_label": ImageFont.truetype(
            str(BASE_DIR / FOOTER_FONT_LOCATION), 14
        ),
    }
    return config


def get_preview_frame(entity, fnt_config) -> Image:
    tournesol_frame = Image.new("RGBA", (440, 240), COLOR_WHITE_BACKGROUND)
    tournesol_frame_draw = ImageDraw.Draw(tournesol_frame)
    full_title = entity.metadata.get("name", "")
    truncated_title = full_title[:200]
    # TODO: optimize this with a dichotomic search
    while (
        tournesol_frame_draw.textlength(
            truncated_title, font=fnt_config["entity_title"]
        )
        > 300
    ):
        truncated_title = truncated_title[:-4] + "..."
    full_uploader = entity.metadata.get("uploader", "")
    truncated_uploader = full_uploader[:200]
    # TODO: optimize this with a dichotomic search
    while (
        tournesol_frame_draw.textlength(
            truncated_uploader, font=fnt_config["entity_title"]
        )
        > 300
    ):
        truncated_uploader = truncated_uploader[:-4] + "..."

    tournesol_frame_draw.text(
        ENTITY_TITLE_XY,
        truncated_uploader,
        font=fnt_config["entity_uploader"],
        fill=COLOR_BROWN_FONT,
    )
    tournesol_frame_draw.text(
        (ENTITY_TITLE_XY[0], ENTITY_TITLE_XY[1] + 24),
        truncated_title,
        font=fnt_config["entity_title"],
        fill=COLOR_BROWN_FONT,
    )

    score = entity.tournesol_score
    if score is not None:
        score_color = COLOR_BROWN_FONT
        score_xy = TOURNESOL_SCORE_XY

        if score <= 0:
            score_color = COLOR_NEGATIVE_SCORE
            score_xy = TOURNESOL_SCORE_NEGATIVE_XY

        tournesol_frame_draw.text(
            score_xy,
            f"{score:.0f}",
            font=fnt_config["ts_score"],
            fill=score_color,
            anchor="mt",
        )
    x_coordinate, y_coordinate = ENTITY_N_CONTRIBUTORS_XY
    tournesol_frame_draw.text(
        (x_coordinate, y_coordinate),
        f"{entity.rating_n_ratings}",
        font=fnt_config["entity_ratings"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.text(
        (x_coordinate, y_coordinate + 26),
        "comparisons",
        font=fnt_config["entity_ratings_label"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.text(
        (x_coordinate, y_coordinate + 82),
        f"{entity.rating_n_contributors}",
        font=fnt_config["entity_ratings"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.text(
        (x_coordinate, y_coordinate + 108),
        "contributors",
        font=fnt_config["entity_ratings_label"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.rectangle(((113, 0), (119, 240)), fill=COLOR_YELLOW_BORDER)
    tournesol_frame_draw.rectangle(((119, 180), (440, 186)), fill=COLOR_YELLOW_BORDER)
    return tournesol_frame


class DynamicWebsitePreviewDefault(BasePreviewAPIView):
    """
    Return the default preview of the Tournesol front end.
    """

    permission_classes = []

    @method_decorator(cache_page_no_i18n(3600 * 24))  # 24h cache
    @extend_schema(
        description="Default website preview.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        return self.default_preview()


class DynamicWebsitePreviewEntity(BasePreviewAPIView):
    """
    Return a preview of an entity, with its Tournesol score, comparisons and
    contributors.
    """

    permission_classes = []

    def _draw_logo(self, image: Image, entity: Entity):
        """
        Draw the Tournesol logo on the provided image.

        If the Tournesol score of the entity is negative, nothing is drawn.
        """
        # Negative scores are displayed without the Tournesol logo, to have
        # more space to display the minus symbol, and to make it clear that
        # the entity is not currently trusted by Tournesol.
        score = entity.tournesol_score

        # If the score has not been computed yet, display a centered flower.
        if score is None:
            image.alpha_composite(self.get_ts_logo(34), dest=(43, 24))

        # If the score has been computed, and is positive, display the flower
        # just before the score.
        if score and score > 0:
            image.alpha_composite(self.get_ts_logo(34), dest=(16, 24))

    # TODO: should this cache be enabled?
    @method_decorator(cache_page_no_i18n(0 * 2))  # 2h cache
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

        response = HttpResponse(content_type="image/png")
        preview_image = get_preview_frame(entity, get_preview_font_config())

        try:
            youtube_thumbnail = self.get_yt_thumbnail(entity)
        except ConnectionError:
            return self.default_preview()

        preview_image.paste(youtube_thumbnail, box=(120, 0))
        self._draw_logo(preview_image, entity)
        preview_image.save(response, "png")
        return response
