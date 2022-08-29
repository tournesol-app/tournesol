import logging
from io import BytesIO

import requests
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiTypes, extend_schema
from PIL import Image, ImageDraw, ImageFont
from rest_framework.views import APIView

from tournesol.entities.video import TYPE_VIDEO
from tournesol.models.entity import Entity
from tournesol.utils.cache import cache_page_no_i18n

logger = logging.getLogger(__name__)

BASE_DIR = settings.BASE_DIR

FOOTER_FONT_LOCATION = "tournesol/resources/Poppins-Medium.ttf"
ENTITY_N_CONTRIBUTORS_YX = (60, 98)
ENTITY_TITLE_XY = (128, 190)

TOURNESOL_SCORE_XY = (84, 30)
TOURNESOL_SCORE_NEGATIVE_XY = (60, 30)

COLOR_YELLOW_BORDER = (255, 200, 0, 255)
COLOR_YELLOW_BACKGROUND = (255, 200, 0, 16)
COLOR_WHITE_BACKGROUND = (255, 250, 230, 255)
COLOR_BROWN_FONT = (29, 26, 20, 255)
COLOR_NEGATIVE_SCORE = (128, 128, 128, 248)


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
    tournesol_footer = Image.new("RGBA", (440, 240), COLOR_WHITE_BACKGROUND)
    tournesol_footer_draw = ImageDraw.Draw(tournesol_footer)
    full_title = entity.metadata.get("name", "")
    truncated_title = full_title[:200]
    # TODO: optimize this with a dichotomic search
    while (
        tournesol_footer_draw.textlength(
            truncated_title, font=fnt_config["entity_title"]
        )
        > 300
    ):
        truncated_title = truncated_title[:-4] + "..."
    full_uploader = entity.metadata.get("uploader", "")
    truncated_uploader = full_uploader[:200]
    # TODO: optimize this with a dichotomic search
    while (
        tournesol_footer_draw.textlength(
            truncated_uploader, font=fnt_config["entity_title"]
        )
        > 300
    ):
        truncated_uploader = truncated_uploader[:-4] + "..."

    tournesol_footer_draw.text(
        ENTITY_TITLE_XY,
        truncated_uploader,
        font=fnt_config["entity_uploader"],
        fill=COLOR_BROWN_FONT,
    )
    tournesol_footer_draw.text(
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

        tournesol_footer_draw.text(
            score_xy,
            "%.0f" % score,
            font=fnt_config["ts_score"],
            fill=score_color,
            anchor="mt",
        )
        x, y = ENTITY_N_CONTRIBUTORS_YX
        tournesol_footer_draw.text(
            (x, y),
            f"{entity.rating_n_ratings}",
            font=fnt_config["entity_ratings"],
            fill=COLOR_BROWN_FONT,
            anchor="mt",
        )
        tournesol_footer_draw.text(
            (x, y + 26),
            "comparisons",
            font=fnt_config["entity_ratings_label"],
            fill=COLOR_BROWN_FONT,
            anchor="mt",
        )
        tournesol_footer_draw.text(
            (x, y + 82),
            f"{entity.rating_n_contributors}",
            font=fnt_config["entity_ratings"],
            fill=COLOR_BROWN_FONT,
            anchor="mt",
        )
        tournesol_footer_draw.text(
            (x, y + 108),
            "contributors",
            font=fnt_config["entity_ratings_label"],
            fill=COLOR_BROWN_FONT,
            anchor="mt",
        )
        tournesol_footer_draw.rectangle(((113, 0), (119, 240)), fill=COLOR_YELLOW_BORDER)
        tournesol_footer_draw.rectangle(((119, 180), (440, 186)), fill=COLOR_YELLOW_BORDER)
    return tournesol_footer


class DynamicWebsitePreviewDefault(APIView):
    permission_classes = []

    @method_decorator(cache_page_no_i18n(3600 * 24))  # 24h cache
    @extend_schema(
        description="Default website preview",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        return DynamicWebsitePreviewDefault.default_preview()

    @staticmethod
    def default_preview():
        default_preview = open(
            str(BASE_DIR / "tournesol/resources/tournesol_screenshot_og.png"), "rb"
        )
        response = FileResponse(default_preview, content_type="image/png")
        return response


class DynamicWebsitePreviewEntity(APIView):
    permission_classes = []

    @method_decorator(cache_page_no_i18n(0 * 2))  # 2h cache
    @extend_schema(
        description="Website preview for entities page",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, uid):
        try:
            entity = Entity.objects.get(uid=uid)
        except Entity.DoesNotExist as e:
            logger.error(f"Preview impossible entity with UID {uid}.")
            logger.error(f"Exception caught: {e}")
            return DynamicWebsitePreviewDefault.default_preview()

        if entity.type != TYPE_VIDEO:
            logger.info(f"Preview not implemented for entity with UID {entity.uid}.")
            return DynamicWebsitePreviewDefault.default_preview()

        response = HttpResponse(content_type="image/png")
        preview_image = get_preview_frame(entity, get_preview_font_config())
        url = f"https://img.youtube.com/vi/{entity.video_id}/mqdefault.jpg"

        try:
            thumbnail_response = requests.get(url)
        except ConnectionError as e:
            logger.error(f"Preview impossible entity with UID {uid}.")
            logger.error(f"Exception caught: {e}")
            return DynamicWebsitePreviewDefault.default_preview()

        if thumbnail_response.status_code != 200:
            # We chose to not raise an error here because the responses often
            # have a non-200 status while containing the right content (e.g.
            # 304, 443).
            # raise ConnectionError
            logger.warning(
                f"Fetching YouTube thumbnail has non-200 status: {thumbnail_response.status_code}"
            )

        youtube_thumbnail = Image.open(BytesIO(thumbnail_response.content)).convert(
            "RGBA"
        )

        # Merge the two images into one.
        preview_image.paste(youtube_thumbnail, box=(120, 0))

        # Negative scores are displayed without the Tournesol logo, to have
        # more space to display the minus symbol, and to make it clear that
        # the entity is not currently trusted by Tournesol.
        score = entity.tournesol_score
        if score and score > 0:
            logo_image = (
                Image.open(BASE_DIR / "tournesol/resources/Logo64.png")
                .convert("RGBA")
                .resize((34, 34))
            )
            preview_image.alpha_composite(logo_image, dest=(16, 24))

        preview_image.save(response, "png")
        return response
