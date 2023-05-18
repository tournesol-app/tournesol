"""
API returning preview images of some Tournesol recommendations page.

Mainly used to provide URLs that can be used by the Open Graph protocol.
"""
import datetime

import numpy
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiTypes, extend_schema
from PIL import Image, ImageDraw
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.exceptions import NotFound

from tournesol.models import Poll
from tournesol.renderers import ImageRenderer
from tournesol.utils.cache import cache_page_no_i18n

from ..views import PollsRecommendationsView
from ..views.preview import (
    COLOR_BROWN_FONT,
    COLOR_GREY_FONT,
    COLOR_WHITE_BACKGROUND,
    COLOR_WHITE_FONT,
    COLOR_YELLOW_BORDER,
    BasePreviewAPIView,
    DynamicWebsitePreviewEntity,
    get_preview_font_config,
)

TOURNESOL_RECOMMENDATIONS_HEADLINE_XY = (8, 3)

CACHE_RECOMMENDATIONS_PREVIEW = 3600 * 2
DAY_IN_SECS = 60 * 60 * 24

DATE_PARAM_TO_SECONDS_MAX_AGE = {
    "Today": DAY_IN_SECS * 1.5,
    "Week": DAY_IN_SECS * 7,
    "Month": DAY_IN_SECS * 31,
    "Year": DAY_IN_SECS * 365,
}


@extend_schema(
    responses={(200, "image/jpeg"): OpenApiTypes.BINARY},
)
@api_view()
@permission_classes([])
@renderer_classes([ImageRenderer])
def get_preview_recommendations_redirect_params(request):
    """
    Preview of a Recommendations page.
    Returns HTTP redirection to transform the query parameters into the format used by the backend.
    """
    params = request.GET
    query = QueryDict("", mutable=True)

    for (key, value) in params.items():
        if key == "language":
            languages = value.split(",")
            if languages:
                query.setlist("metadata[language]", languages)
        elif key == "date":
            if value in DATE_PARAM_TO_SECONDS_MAX_AGE:
                seconds_max_age = DATE_PARAM_TO_SECONDS_MAX_AGE[value]
                now = timezone.now()
                date_gte = now - datetime.timedelta(seconds=seconds_max_age)
                query["date_gte"] = date_gte.isoformat(timespec="seconds")
        else:
            query[key] = params[key]

    redirect_base_url = reverse("tournesol:website_preview_recommendations_internal")
    return HttpResponseRedirect(f"{redirect_base_url}?{query.urlencode()}")


class DynamicWebsitePreviewRecommendations(BasePreviewAPIView, PollsRecommendationsView):
    """
    Return a preview of the Tournesol front end's recommendations page.
    """

    upscale_ratio = 2
    fnt_config = get_preview_font_config(upscale_ratio)

    # overwrite the default method of `PollScopedViewMixin`
    def poll_from_kwargs_or_404(self, request_kwargs):
        poll_name = "videos"
        try:
            return Poll.objects.get(name=poll_name)
        except Poll.DoesNotExist as error:
            raise NotFound(f"The requested poll {poll_name} doesn't exist.") from error

    def draw_headline(self, image: Image, upscale_ratio: int):
        """
        Draw find videos on Tournesol headline
        """
        headline_height = 30
        border_width = 6
        headline = Image.new(
            "RGBA", (440 * upscale_ratio, headline_height * upscale_ratio), COLOR_WHITE_BACKGROUND
        )
        tournesol_frame_draw = ImageDraw.Draw(headline)

        headline_border = Image.new(
            "RGBA", (440 * upscale_ratio, border_width * upscale_ratio), COLOR_YELLOW_BORDER
        )
        headline_border_position = (0, (headline_height - border_width) * upscale_ratio)

        headline.paste(headline_border, headline_border_position)

        full_title = "Find videos on Tournesol"
        tournesol_frame_draw.text(
            numpy.multiply(TOURNESOL_RECOMMENDATIONS_HEADLINE_XY, upscale_ratio),
            full_title,
            font=self.fnt_config["recommendations_headline"],
            fill="#4a473e",
        )

        image.paste(headline)

    def draw_bottom_overlay(self, image: Image, upscale_ratio: int):
        """
        Draw the bottom overlay showing there is more results
        """
        overlay_width = 440 * upscale_ratio
        overlay_height = 60 * upscale_ratio
        gradient = Image.new("RGBA", (1, overlay_height), color=0xFFF)
        for y_pos in range(overlay_height):
            gradient.putpixel(
                (0, overlay_height - 1 - y_pos),
                (255, 255, 255, int(255 * (1 - y_pos / overlay_height))),
            )
        gradient = gradient.resize((overlay_width, overlay_height))
        overlay_position = (0, (240 * upscale_ratio - overlay_height))
        image.alpha_composite(gradient, dest=overlay_position)

    def draw_recommendation_box(self, recommendation, image: Image, upscale_ratio: int, position):
        box = Image.new("RGBA", (440 * upscale_ratio, 60 * upscale_ratio))
        box_draw = ImageDraw.Draw(box)
        box_draw.rectangle(
            ((0, 0), (440 * upscale_ratio, 60 * upscale_ratio)),
            outline="lightgrey",
            fill=COLOR_WHITE_FONT,
            width=2,
        )

        thumbnail = self.get_yt_thumbnail(recommendation)
        new_width = 105 * upscale_ratio
        new_height = 59 * upscale_ratio
        thumbnail = thumbnail.resize((new_width, new_height), Image.LANCZOS)

        draw_duration = DynamicWebsitePreviewEntity.draw_duration
        thumbnail_bbox = tuple(numpy.multiply((105, 59, 0, 0), upscale_ratio))
        draw_duration(self, thumbnail, recommendation, thumbnail_bbox, upscale_ratio=1)

        box.paste(thumbnail, (1, 1))

        self.draw_video_metadata_box(recommendation, box, upscale_ratio)
        self.draw_tournesol_score_box(recommendation, box, upscale_ratio)
        image.paste(box, position)

    def draw_video_metadata_box(self, video, image: Image, upscale_ratio):
        video_metadata_box = Image.new(
            "RGBA", (330 * upscale_ratio, 40 * upscale_ratio), COLOR_WHITE_FONT
        )
        draw = ImageDraw.Draw(video_metadata_box)

        views_number = f'{video.metadata["views"]:,} views'
        # Expected date format are 2022-06-19T00:00:00Z or 2022-06-19
        publication_date = video.metadata["publication_date"].split("T")[0]

        views_number_width = draw.textlength(
            views_number, self.fnt_config["recommendations_metadata"]
        )
        publication_date_width = draw.textlength(
            publication_date, self.fnt_config["recommendations_metadata"]
        )

        gap = 8 * upscale_ratio
        publication_date_x_gap = views_number_width + gap

        # Draw video title
        draw.text(
            (0, 0),
            video.metadata.get("name", ""),
            font=self.fnt_config["recommendations_title"],
            fill=COLOR_BROWN_FONT,
        )

        # Draw metadata on 2nd line
        second_line_y = 14
        draw.text(
            (0, second_line_y * upscale_ratio),
            views_number,
            font=self.fnt_config["recommendations_metadata"],
            fill=COLOR_GREY_FONT,
        )
        draw.text(
            (publication_date_x_gap, second_line_y * upscale_ratio),
            publication_date,
            font=self.fnt_config["recommendations_metadata"],
            fill=COLOR_GREY_FONT,
        )
        draw.text(
            (
                publication_date_x_gap + publication_date_width + gap,
                second_line_y * upscale_ratio,
            ),
            video.metadata.get("uploader", ""),
            font=self.fnt_config["recommendations_metadata"],
            fill=COLOR_GREY_FONT,
        )

        image.paste(video_metadata_box, (110 * upscale_ratio, 3 * upscale_ratio))

    def draw_tournesol_score_box(self, recommendation, image: Image, upscale_ratio: int):
        ts_score_box = Image.new(
            "RGBA", (300 * upscale_ratio, 20 * upscale_ratio), COLOR_WHITE_FONT
        )
        ts_score_box_draw = ImageDraw.Draw(ts_score_box)

        ts_logo_size = (12 * upscale_ratio, 12 * upscale_ratio)
        ts_logo = self.get_ts_logo(ts_logo_size)
        ts_score = recommendation.tournesol_score
        is_safe = (
            ts_score > 0
            and recommendation.rating_n_contributors >= settings.RECOMMENDATIONS_MIN_CONTRIBUTORS
        )

        ts_score_box.alpha_composite(
            ts_logo if is_safe else ts_logo.convert("LA").convert("RGBA"),
            dest=(0, 0),
        )

        score = str(round(ts_score))

        comparisons = f"{recommendation.rating_n_ratings} comparisons by "
        comparisons_width = ts_score_box_draw.textlength(
            comparisons, self.fnt_config["recommendations_rating"]
        )

        score_x_gap = ts_logo_size[0] + 2 * upscale_ratio
        comparisons_x_gap = score_x_gap + 36 * upscale_ratio

        ts_score_box_draw.text(
            (score_x_gap, -5 * upscale_ratio),
            score,
            font=self.fnt_config["recommendations_ts_score"],
            fill=COLOR_BROWN_FONT,
        )

        ts_score_box_draw.text(
            (comparisons_x_gap, 2 * upscale_ratio),
            comparisons,
            font=self.fnt_config["recommendations_rating"],
            fill=COLOR_GREY_FONT,
        )

        ts_score_box_draw.text(
            (comparisons_x_gap + comparisons_width, 2 * upscale_ratio),
            f"{recommendation.rating_n_contributors} contributors",
            font=self.fnt_config["recommendations_rating"],
            fill="#B38B00",
        )

        image.paste(ts_score_box, (110 * upscale_ratio, 36 * upscale_ratio))

    def draw_no_recommendations_text(self, image: Image):
        draw = ImageDraw.Draw(image)
        text = "No video corresponds to search criteria."
        text_width = draw.textlength(text, self.fnt_config["recommendations_headline"])
        text_pos = ((image.size[0] - text_width) / 2, (image.size[1] - 20*self.upscale_ratio) / 2)
        draw.text(
            text_pos,
            text,
            font=self.fnt_config["recommendations_headline"],
            fill=COLOR_BROWN_FONT,
        )

    @method_decorator(cache_page_no_i18n(CACHE_RECOMMENDATIONS_PREVIEW))
    @extend_schema(exclude=True)
    def get(self, request, *args, **kwargs):
        upscale_ratio = self.upscale_ratio

        preview_image = Image.new("RGBA", (440 * upscale_ratio, 240 * upscale_ratio), "#FAFAFA")

        recommendations = super().get_queryset()[:3]
        recommendation_x_pos = 10 * upscale_ratio

        self.draw_headline(preview_image, upscale_ratio)

        if recommendations:
            for idx, recommendation in enumerate(recommendations):
                recommendation_y_pos = (40 + idx * 70) * upscale_ratio
                self.draw_recommendation_box(
                    recommendation,
                    preview_image,
                    upscale_ratio,
                    (recommendation_x_pos, recommendation_y_pos),
                )
        else:
            self.draw_no_recommendations_text(preview_image)

        self.draw_bottom_overlay(preview_image, upscale_ratio)
        response = HttpResponse(content_type="image/jpeg")
        preview_image.convert("RGB").save(response, "jpeg")
        return response
