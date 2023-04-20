"""
API returning preview images of some Tournesol recommendations page.

Mainly used to provide URLs that can be used by the Open Graph protocol.
"""
import datetime
import time

import numpy
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from drf_spectacular.utils import  OpenApiTypes, extend_schema
from PIL import Image, ImageDraw
from rest_framework.exceptions import NotFound

from tournesol.utils.cache import cache_page_no_i18n
from tournesol.models import Poll

from ..views import PollsRecommendationsView
from ..views.preview import (
    COLOR_BROWN_FONT,
    COLOR_DURATION_RECTANGLE,
    COLOR_GREY_FONT,
    COLOR_WHITE_BACKGROUND,
    COLOR_WHITE_FONT,
    COLOR_YELLOW_BORDER,
    BasePreviewAPIView,
    DynamicWebsitePreviewEntity,
    get_preview_font_config,
)

TOURNESOL_RECOMMENDATIONS_HEADLINE_XY = (15, 3)

CACHE_RECOMMENDATIONS_PREVIEW = 3600 * 12
DAY_IN_SECS = 60 * 60 * 24

CONVERSION_TIME = {
    'Today':  DAY_IN_SECS * 1.5,
    'Week': DAY_IN_SECS * 7,
    'Month': DAY_IN_SECS * 31,
    'Year': DAY_IN_SECS * 365
    }


def format_preview_recommendations(request):
    """
    format the url and redirect
    """
    params = request.GET
    url = '/preview/recommendations-preview?'

    for key in params:
        if key == 'language':
            for lang in params[key].split(','):
                url += f'&metadata[language]={lang}'
        elif key == 'date':
            for time_key in CONVERSION_TIME:
                if params[key] == time_key:
                    now = time.time()
                    date_gte = datetime.datetime.fromtimestamp(now - CONVERSION_TIME[params[key]])
                    url += f'date_gte={date_gte}'
        else:
            url += f'&{key}={params[key]}'

    return HttpResponseRedirect(url)


class DynamicWebsitePreviewRecommendations(BasePreviewAPIView, PollsRecommendationsView):
    """
    Return a preview of the Tournesol front end's recommendations page.
    """

    permission_classes = []
    upscale_ratio = 3
    fnt_config = get_preview_font_config(upscale_ratio)

    # overwrite the default method of `PollScopedViewMixin`
    def poll_from_kwargs_or_404(self, request_kwargs):
        poll_name = "videos"
        try:
            return Poll.objects.get(name=poll_name)
        except ObjectDoesNotExist as error:
            raise NotFound(f"The requested poll {poll_name} doesn't exist.") from error

    def draw_headline(self, image: Image, upscale_ratio: int):
        """
        Draw find videos on Tournesol headline
        """
        # make a blank image for the text, initialized to transparent text color
        headline = Image.new(
            "RGBA", (440 * upscale_ratio, 25 * upscale_ratio), COLOR_WHITE_BACKGROUND
        )
        tournesol_frame_draw = ImageDraw.Draw(headline)

        headline_border = Image.new(
            "RGBA", (440 * upscale_ratio, 3 * upscale_ratio), COLOR_YELLOW_BORDER
        )
        headline_border_position = (0, 22 * upscale_ratio)

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

        overlay = Image.new(
            "RGBA", (440 * upscale_ratio, 25 * upscale_ratio), COLOR_DURATION_RECTANGLE
        )
        overlay.putalpha(127)
        overlay_position = (0, 215 * upscale_ratio)

        image.alpha_composite(
                overlay,
                dest=overlay_position,
            )

    def draw_recommendation_box(
            self, recommendation,
            image: Image, upscale_ratio: int,
            position):

        box = Image.new(
            "RGBA", (440 * upscale_ratio, 60 * upscale_ratio)
        )
        box_draw = ImageDraw.Draw(box)

        box_draw.rectangle(
            ((0, 0), (440 * upscale_ratio, 60 * upscale_ratio)),
            outline="lightgrey",
            fill=COLOR_WHITE_FONT,
            width=2,
        )

        thumbnail = self.get_yt_thumbnail(recommendation)
        new_width = 106 * upscale_ratio
        new_height = 59 * upscale_ratio
        thumbnail = thumbnail.resize((new_width, new_height), Image.LANCZOS)

        draw_duration = DynamicWebsitePreviewEntity.draw_duration
        thumbnail_bbox = tuple(numpy.multiply((106, 59, 0, 0), upscale_ratio))
        draw_duration(self, thumbnail, recommendation, thumbnail_bbox, 2)

        box.paste(thumbnail, (1, 1))

        self.draw_video_metadata_box(recommendation, box, upscale_ratio)
        self.draw_tournesol_score_box(recommendation, box, upscale_ratio)

        image.paste(box, position)

        return True

    def draw_video_metadata_box(self, video, image: Image, upscale_ratio):
        video_metadata_box = Image.new(
            "RGBA", (330 * upscale_ratio, 40 * upscale_ratio), COLOR_WHITE_FONT
        )
        draw = ImageDraw.Draw(video_metadata_box)

        title = video.metadata['name']
        views_number = f'{video.metadata["views"]:,} views'
        # Expected date format are 2022-06-19T00:00:00Z or 2022-06-19
        publication_date = video.metadata["publication_date"].split('T')[0]
        uploader = video.metadata["uploader"]

        views_number_size = draw.textsize(
                views_number,
                self.fnt_config["recommendations_metadata"]
            )

        publication_date_size = draw.textsize(
                publication_date,
                self.fnt_config["recommendations_metadata"]
            )

        gap = 4 * upscale_ratio
        publication_date_x_gap = views_number_size[0] + gap
        uploader_x_gap = publication_date_x_gap + publication_date_size[0] + gap

        draw.text(
            (0, 0),
            title,
            font=self.fnt_config["recommendations_title"],
            fill=COLOR_BROWN_FONT,
        )

        draw.text(
            (0, 9 * upscale_ratio),
            views_number,
            font=self.fnt_config["recommendations_metadata"],
            fill=COLOR_GREY_FONT,
        )

        draw.text(
            (publication_date_x_gap, 9 * upscale_ratio),
            publication_date,
            font=self.fnt_config["recommendations_metadata"],
            fill=COLOR_GREY_FONT,
        )

        draw.text(
            (uploader_x_gap, 9 * upscale_ratio),
            uploader,
            font=self.fnt_config["recommendations_metadata"],
            fill=COLOR_GREY_FONT,
        )

        image.paste(video_metadata_box, (110 * upscale_ratio, 5 * upscale_ratio))

    def draw_tournesol_score_box(self, recommendation, image: Image, upscale_ratio: int):

        ts_score_box = Image.new(
            "RGBA", (200 * upscale_ratio, 20 * upscale_ratio), COLOR_WHITE_FONT
        )
        ts_score_box_draw = ImageDraw.Draw(ts_score_box)

        ts_logo_size = (12 * upscale_ratio, 12 * upscale_ratio)
        ts_logo = self.get_ts_logo(ts_logo_size)
        ts_score_box.alpha_composite(
                ts_logo,
                dest=(0, 0),
            )

        score = str(round(recommendation.tournesol_score))
        comparisons = str(recommendation.rating_n_ratings) + ' comparisons by '
        contributors = str(recommendation.rating_n_contributors) + ' contributors'

        score_size = ts_score_box_draw.textsize(score, self.fnt_config["entity_title"])
        comparisons_size = ts_score_box_draw.textsize(
            comparisons,
            self.fnt_config["recommendations_rating"]
            )

        score_x_gap = ts_logo_size[0]
        comparisons_x_gap = score_x_gap + score_size[0] + 2 * upscale_ratio

        ts_score_box_draw.text(
            (score_x_gap, -4 * upscale_ratio),
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
            (comparisons_x_gap + comparisons_size[0], 2 * upscale_ratio),
            contributors,
            font=self.fnt_config["recommendations_rating"],
            fill="#B38B00",
        )

        image.paste(ts_score_box, (110 * upscale_ratio, 25 * upscale_ratio))

    def draw_no_recommendations_text(self, image: Image):
        draw = ImageDraw.Draw(image)
        text_size = draw.textsize(
            'No video corresponds to this search criteria.',
            self.fnt_config["recommendations_headline"]
        )
        text_pos = ((image.size[0] - text_size[0]) / 2, (image.size[1] - text_size[1]) / 2)
        draw.text(
            text_pos,
            'No video corresponds to this search criteria.',
            font=self.fnt_config["recommendations_headline"],
            fill=COLOR_BROWN_FONT,
        )

    @method_decorator(cache_page_no_i18n(CACHE_RECOMMENDATIONS_PREVIEW))
    @extend_schema(
        description="Recommendations page preview.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="image/png")

        upscale_ratio = self.upscale_ratio

        preview_image = Image.new(
            "RGBA", (440 * upscale_ratio, 240 * upscale_ratio), '#FAFAFA'
        )

        recommendations = super().get_queryset()[:3]
        recommendation_x_pos = 20 * upscale_ratio
        i = 0

        self.draw_headline(preview_image, upscale_ratio)

        if recommendations:
            for recommendation in recommendations:
                recommendation_y_pos = (40 + i * 70) * upscale_ratio
                self.draw_recommendation_box(
                    recommendation,
                    preview_image,
                    upscale_ratio,
                    (recommendation_x_pos, recommendation_y_pos)
                )
                i += 1
        else:
            self.draw_no_recommendations_text(preview_image)
            preview_image.save(response, "png")
            return response

        self.draw_bottom_overlay(preview_image, upscale_ratio)

        preview_image.save(response, "png")

        return response
