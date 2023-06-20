"""
API returning preview images of comparisons.
"""
import numpy
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from PIL import Image, ImageDraw, ImageFont
from rest_framework.views import APIView

from settings.settings import BASE_DIR
from tournesol.models import Entity
from tournesol.utils.cache import cache_page_no_i18n

from .default import (
    CACHE_ENTITY_PREVIEW,
    COLOR_BROWN_FONT,
    COLOR_WHITE_BACKGROUND,
    COLOR_YELLOW_BORDER,
    FOOTER_FONT_LOCATION,
    BasePreviewAPIView,
    font_height,
    truncate_text,
)


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
