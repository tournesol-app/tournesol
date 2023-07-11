"""
API returning preview images of frequently asked questions.
"""
import textwrap

import numpy
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from PIL import Image, ImageDraw

from backoffice.models import FAQEntry
from tournesol.utils.cache import cache_page_no_i18n

from .default import (
    CACHE_DEFAULT_PREVIEW,
    COLOR_WHITE_FONT,
    BasePreviewAPIView,
    get_headline,
    get_preview_font_config,
)

FAQ_HEADLINE_XY = (30, 3)
FAQ_TOURNESOL_TITLE_XY = (128, 194)
FAQ_UPSCALE_RATIO = 2


class DynamicWebsitePreviewFAQ(BasePreviewAPIView):
    """
    Return a preview of a question.
    """

    permission_classes = []

    fnt_config = get_preview_font_config(upscale_ratio=FAQ_UPSCALE_RATIO)

    def _draw_logo(self, image: Image.Image, upscale_ratio: int):
        image.alpha_composite(
            self.get_ts_logo(tuple(numpy.multiply((20, 20), upscale_ratio))),
            dest=tuple(numpy.multiply((5, 3), upscale_ratio)),
        )

    def draw_header(self, image: Image.Image, upscale_ratio: int):
        headline = get_headline(upscale_ratio)

        tournesol_frame_draw = ImageDraw.Draw(headline)
        tournesol_frame_draw.text(
            tuple(numpy.multiply(FAQ_HEADLINE_XY, upscale_ratio)),
            "FAQ Tournesol",
            font=self.fnt_config["faq_headline"],
            fill="#4a473e",
        )

        image.paste(headline)
        self._draw_logo(image, upscale_ratio)

    def draw_question(self, image: Image.Image, title, upscale_ratio: int):
        headline_height = 30
        text_box_image = Image.new(
            "RGBA",
            (440 * upscale_ratio, (240 - headline_height) * upscale_ratio),
            COLOR_WHITE_FONT,
        )
        text_box = ImageDraw.Draw(text_box_image)

        title_lines = textwrap.wrap(title, width=34)
        line_height = 24
        line_nb = 0
        for line in title_lines:
            text_box.text(
                tuple(numpy.multiply((0, line_height * line_nb), upscale_ratio)),
                line,
                font=self.fnt_config["faq_question"],
                fill="#4a473e",
            )
            line_nb += 1

        image.paste(
            text_box_image,
            (30, int(1 / 2 * ((240 - line_height * len(title_lines)) * upscale_ratio))),
        )

    @method_decorator(cache_page_no_i18n(CACHE_DEFAULT_PREVIEW))
    @extend_schema(
        description="FAQ preview",
        responses={200: OpenApiTypes.BINARY},
        parameters=[
            OpenApiParameter(
                "scrollTo",
                OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ],
    )
    def get(self, request):
        scroll_to = request.query_params.get("scrollTo")
        if scroll_to is None:
            return self.default_preview()

        upscale_ratio = FAQ_UPSCALE_RATIO
        try:
            question = FAQEntry.objects.get(name=scroll_to)
        except FAQEntry.DoesNotExist:
            return self.default_preview()

        if not question.enabled:
            return self.default_preview()

        title = question.get_localized_text(related="questions", field="text")

        preview_image = Image.new(
            "RGBA", (440 * upscale_ratio, 240 * upscale_ratio), COLOR_WHITE_FONT
        )
        self.draw_header(preview_image, upscale_ratio)
        self.draw_question(preview_image, title, upscale_ratio)

        response = HttpResponse(content_type="image/jpeg")
        preview_image.convert("RGB").save(response, "jpeg")
        return response
