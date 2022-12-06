"""
API returning preview images of some Tournesol front end's page.

Mainly used to provide URLs that can be used by the Open Graph protocol.
"""

import logging
from io import BytesIO

import numpy
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

CACHE_DEFAULT_PREVIEW = 3600 * 24  # 24h
CACHE_ENTITY_PREVIEW = 3600 * 2

FOOTER_FONT_LOCATION = "tournesol/resources/Poppins-Medium.ttf"
ENTITY_N_CONTRIBUTORS_XY = (60, 98)
ENTITY_TITLE_XY = (128, 194)

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
        # The file needs to remain open to be streamed and will be closed automatically
        # by FileResponse. A context-manager should not be used here.
        # pylint: disable=consider-using-with
        default_preview = open(
            str(BASE_DIR / "tournesol/resources/tournesol_screenshot_og.png"), "rb"
        )
        return FileResponse(default_preview, content_type="image/png")

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

    def get_ts_logo(self, size: tuple):
        return (
            Image.open(BASE_DIR / "tournesol/resources/Logo64.png")
            .convert("RGBA")
            .resize(size)
        )

    def get_yt_thumbnail(self, entity: Entity, quality="mq") -> Image:
        # Quality can be: hq, mq, sd, or maxres (https://stackoverflow.com/a/34784842/188760)
        url = f"https://img.youtube.com/vi/{entity.video_id}/{quality}default.jpg"
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


def get_preview_frame(entity, fnt_config, upscale_ratio=1) -> Image:
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
        numpy.multiply(ENTITY_TITLE_XY, upscale_ratio),
        truncated_uploader,
        font=fnt_config["entity_uploader"],
        fill=COLOR_BROWN_FONT,
    )
    tournesol_frame_draw.text(
        numpy.multiply((ENTITY_TITLE_XY[0], ENTITY_TITLE_XY[1] + 18), upscale_ratio),
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
            numpy.multiply(score_xy, upscale_ratio),
            f"{score:.0f}",
            font=fnt_config["ts_score"],
            fill=score_color,
            anchor="mt",
        )
    x_coordinate, y_coordinate = ENTITY_N_CONTRIBUTORS_XY
    tournesol_frame_draw.text(
        numpy.multiply((x_coordinate, y_coordinate), upscale_ratio),
        f"{entity.rating_n_ratings}",
        font=fnt_config["entity_ratings"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.text(
        numpy.multiply((x_coordinate, y_coordinate + 26), upscale_ratio),
        "comparisons",
        font=fnt_config["entity_ratings_label"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.text(
        numpy.multiply((x_coordinate, y_coordinate + 82), upscale_ratio),
        f"{entity.rating_n_contributors}",
        font=fnt_config["entity_ratings"],
        fill=COLOR_BROWN_FONT,
        anchor="mt",
    )
    tournesol_frame_draw.text(
        numpy.multiply((x_coordinate, y_coordinate + 108), upscale_ratio),
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


class DynamicWebsitePreviewEntity(BasePreviewAPIView):
    """
    Return a preview of an entity, with its Tournesol score, comparisons and
    contributors.
    """

    permission_classes = []

    def _draw_logo(self, image: Image, entity: Entity, upscale_ratio: int):
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
            image.alpha_composite(
                self.get_ts_logo(numpy.multiply((34, 34), upscale_ratio)),
                dest=tuple(numpy.multiply((43, 24), upscale_ratio)),
            )

        # If the score has been computed, and is positive, display the flower
        # just before the score.
        if score and score > 0:
            image.alpha_composite(
                self.get_ts_logo(numpy.multiply((34, 34), upscale_ratio)),
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

        response = HttpResponse(content_type="image/png")

        upscale_ratio = 2
        fnt_config = get_preview_font_config(upscale_ratio=upscale_ratio)
        preview_image = get_preview_frame(
            entity, fnt_config, upscale_ratio=upscale_ratio
        )

        try:
            youtube_thumbnail = self.get_yt_thumbnail(entity, quality="maxres")
        except ConnectionError:
            return self.default_preview()

        youtube_thumbnail = youtube_thumbnail.resize(
            numpy.multiply((320, 180), upscale_ratio)
        )
        preview_image.paste(
            youtube_thumbnail, box=tuple(numpy.multiply((120, 0), upscale_ratio))
        )

        self._draw_logo(preview_image, entity, upscale_ratio=upscale_ratio)

        preview_image.save(response, "png")
        return response


class ComparisonPreviewGenerator:
    def __init__(self):
        # An upscale ratio > 1 generates a bigger image while keeping all the relative sizes
        # and positions identical (like a zoom). Only integer values are allowed for now.
        self.upscale_ratio = 2

    def render(self, entity_a, entity_b, thumbnail_a, thumbnail_b):
        # pylint: disable=too-many-locals

        base_size = (440, 240)

        # All the sizes and positions in this method are relative to the base size, not the
        # upscaled size. The other methods are responsible for calculating the final (upscaled)
        # sizes and positions.

        base_margin = 6
        horizontal_separator_height = base_margin
        margin_above_entity_descriptions = base_margin
        entity_descriptions_horizontal_margin = base_margin
        logo_size = 32
        margin_above_slider = base_margin * 3
        margin_below_slider = base_margin
        vs_band_width = 34
        vs_tilt_in_pixels = 10
        text_below_slider = "Which one should be largely recommended?"

        final = self.generate_image(base_size, color=COLOR_WHITE_BACKGROUND)

        thumbnail_a_size = self.draw_thumbnail(
            thumbnail_a,
            target=final,
            position=(0, 0),
            width=base_size[0] // 2,
        )
        thumbnail_b_size = self.draw_thumbnail(
            thumbnail_b,
            target=final,
            position=(base_size[0] // 2, 0),
            width=base_size[0] // 2,
        )
        thumbnail_height = max(
            thumbnail_a_size[1],
            thumbnail_b_size[1],
        )

        self.draw_vs_background(
            target=final,
            band_width=vs_band_width,
            tilt_in_pixels=vs_tilt_in_pixels,
            height=thumbnail_height,
        )
        self.draw_horizontal_separator(
            target=final,
            top=thumbnail_height,
            height=horizontal_separator_height,
        )

        self.draw_text(
            target=final,
            text="VS",
            position=(base_size[0] // 2, thumbnail_height // 2),
            font=self.font(FOOTER_FONT_LOCATION, 20),
            fill=COLOR_BROWN_FONT,
            anchor="mm",
        )

        entity_description_top = (
            thumbnail_height
            + horizontal_separator_height
            + margin_above_entity_descriptions
        )

        self.draw_logo(
            target=final,
            size=logo_size,
            position=(base_size[0] // 2 - logo_size // 2, entity_description_top),
        )

        available_width = (
            base_size[0] // 2
            - logo_size // 2
            - entity_descriptions_horizontal_margin * 2
        )
        entity_a_description_height = self.draw_entity_description(
            entity_a,
            target=final,
            position=(entity_descriptions_horizontal_margin, entity_description_top),
            available_width=available_width,
        )
        entity_b_description_height = self.draw_entity_description(
            entity_b,
            target=final,
            position=(
                (
                    base_size[0] // 2
                    + logo_size // 2
                    + entity_descriptions_horizontal_margin
                ),
                entity_description_top,
            ),
            available_width=available_width,
        )
        entity_description_height = max(
            entity_a_description_height,
            entity_b_description_height,
        )

        slider_top = (
            entity_description_top
            + max(entity_description_height, logo_size)
            + margin_above_slider
        )
        slider_height = self.draw_slider(
            target=final,
            position=(0, slider_top),
        )

        self.draw_text(
            target=final,
            text=text_below_slider,
            position=(
                base_size[0] // 2,
                slider_top + slider_height + margin_below_slider,
            ),
            font=self.font(FOOTER_FONT_LOCATION, 14),
            fill=COLOR_BROWN_FONT,
            anchor="mt",
        )

        return final

    def generate_image(self, base_size, color):
        final_size = tuple(numpy.multiply(base_size, self.upscale_ratio))
        return Image.new("RGBA", final_size, color)

    def font(self, name, size):
        return ImageFont.truetype(str(BASE_DIR / name), size * self.upscale_ratio)

    def load_resource_image(self, filename):
        return Image.open(BASE_DIR / "tournesol/resources" / filename)

    def draw_thumbnail(self, thumbnail, target, position, width):
        original_size = thumbnail.size
        aspect_ratio = original_size[0] / original_size[1]
        scaled_width = width * self.upscale_ratio
        scaled_height = int(scaled_width / aspect_ratio)
        scaled_size = (scaled_width, scaled_height)

        thumbnail = thumbnail.resize(scaled_size)
        target.paste(thumbnail, tuple(numpy.multiply(position, self.upscale_ratio)))

        return numpy.floor_divide(scaled_size, self.upscale_ratio)

    def draw_vs_background(self, target, band_width, tilt_in_pixels, height):
        # We render the background in a larger image to generate anti-alias for the tilted lines
        anti_alias_ratio = 4
        band_width = band_width * self.upscale_ratio * anti_alias_ratio
        tilt_in_pixels = tilt_in_pixels * self.upscale_ratio * anti_alias_ratio
        upscaled_size = tuple(numpy.multiply(target.size, anti_alias_ratio))
        vs_background = Image.new("RGBA", upscaled_size, (0, 0, 0, 0))
        top = 0
        bottom = height * self.upscale_ratio * anti_alias_ratio
        draw = ImageDraw.Draw(vs_background)
        draw.polygon(
            [
                (
                    upscaled_size[0] // 2 + tilt_in_pixels - band_width // 2,
                    top,
                ),
                (
                    upscaled_size[0] // 2 + tilt_in_pixels + band_width // 2,
                    top,
                ),
                (
                    upscaled_size[0] // 2 - tilt_in_pixels + band_width // 2,
                    bottom,
                ),
                (
                    upscaled_size[0] // 2 - tilt_in_pixels - band_width // 2,
                    bottom,
                ),
            ],
            fill=COLOR_YELLOW_BORDER,
            outline=(0, 0, 0),
            width=0,
        )
        target.alpha_composite(vs_background.resize(target.size))

    def draw_horizontal_separator(self, target, top, height):
        draw = ImageDraw.Draw(target)
        draw.rectangle(
            (
                (0, top * self.upscale_ratio),
                (target.size[0], (top + height) * self.upscale_ratio),
            ),
            fill=COLOR_YELLOW_BORDER,
            width=0,
        )

    def draw_text(self, target, text, position, **text_args):
        draw = ImageDraw.Draw(target)
        draw.text(
            numpy.multiply(position, self.upscale_ratio),
            text,
            **text_args,
        )

    def draw_logo(self, target, size, position):
        logo_size = (size * self.upscale_ratio, size * self.upscale_ratio)
        logo = self.load_resource_image("Logo64.png").resize(logo_size)
        dest = tuple(numpy.multiply(position, self.upscale_ratio))
        target.alpha_composite(logo, dest=dest)

    def draw_entity_description(self, entity, target, position, available_width):
        draw = ImageDraw.Draw(target)
        position = numpy.multiply(position, self.upscale_ratio)
        available_width *= self.upscale_ratio

        full_uploader = entity.metadata.get("uploader", "")
        uploader_font = self.font(FOOTER_FONT_LOCATION, 11)
        truncated_uploader = truncate_text(
            draw,
            full_uploader,
            font=uploader_font,
            available_width=available_width,
        )
        draw.text(
            position,
            truncated_uploader,
            font=uploader_font,
            fill=COLOR_BROWN_FONT,
        )
        uploader_height = font_height(uploader_font)

        full_title = entity.metadata.get("name", "")
        title_font = self.font(FOOTER_FONT_LOCATION, 14)
        truncated_title = truncate_text(
            draw,
            full_title,
            font=title_font,
            available_width=available_width,
        )
        draw.text(
            (position[0], position[1] + uploader_height),
            truncated_title,
            font=title_font,
            fill=COLOR_BROWN_FONT,
        )
        title_height = font_height(title_font)

        total_height = (uploader_height + title_height) // self.upscale_ratio
        return total_height

    def draw_slider(self, target, position):
        if self.upscale_ratio == 1:
            comparison_slider = self.load_resource_image("comparison_slider.png")
        elif self.upscale_ratio == 2:
            comparison_slider = self.load_resource_image("comparison_slider-2x.png")
        else:
            comparison_slider = self.load_resource_image("comparison_slider-4x.png")
            comparison_slider = comparison_slider.resize(
                (
                    target.size[0],
                    target.size[0] * 160 // 1760,
                )
            )

        vertical_margin_in_image = 10

        dest = (
            position[0] * self.upscale_ratio,
            (position[1] - vertical_margin_in_image) * self.upscale_ratio,
        )
        target.alpha_composite(
            comparison_slider,
            dest=dest,
        )
        return (
            comparison_slider.size[1] // self.upscale_ratio
            - 2 * vertical_margin_in_image
        )


class DynamicWebsitePreviewComparison(BasePreviewAPIView, APIView):
    """
    Return the preview of the Tournesol front end's comparison page.
    """

    permission_classes = []

    @method_decorator(cache_page_no_i18n(CACHE_ENTITY_PREVIEW))
    @extend_schema(
        description="Preview of the website comparison page.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, uid_a, uid_b):
        try:
            entity_a = self.get_entity(uid_a)
            entity_b = self.get_entity(uid_b)
        except Entity.DoesNotExist:
            return self.default_preview()

        if not self.is_video(entity_a) or not self.is_video(entity_b):
            return self.default_preview()

        thumbnail_quality = "maxres"
        try:
            thumbnail_a = self.get_yt_thumbnail(entity_a, quality=thumbnail_quality)
            thumbnail_b = self.get_yt_thumbnail(entity_b, quality=thumbnail_quality)
        except ConnectionError:
            return self.default_preview()

        generator = ComparisonPreviewGenerator()
        final = generator.render(entity_a, entity_b, thumbnail_a, thumbnail_b)

        response = HttpResponse(content_type="image/png")
        final.save(response, "png")
        return response
