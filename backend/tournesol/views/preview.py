import logging
from io import BytesIO

import requests
from django.http import FileResponse, HttpResponse
from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiTypes, extend_schema
from PIL import Image, ImageDraw, ImageFont
from rest_framework.views import APIView

from tournesol.models.entity import Entity
from tournesol.utils.cache import cache_page_no_i18n

logger = logging.getLogger(__name__)


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
        default_preview = open("tournesol/resources/tournesol_screenshot_og.png", "rb")
        response = FileResponse(default_preview, content_type="image/png")
        return response


class DynamicWebsitePreviewEntity(APIView):
    permission_classes = []

    @method_decorator(cache_page_no_i18n(3600 * 2))  # 2h cache
    @extend_schema(
        description="Website preview for entities page",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, uid):
        fnt = ImageFont.truetype("tournesol/resources/Poppins-Medium.ttf", 20)
        fnt_title = ImageFont.truetype("tournesol/resources/Poppins-Medium.ttf", 14)

        try:
            entity = Entity.objects.get(uid=uid)
            response = HttpResponse(content_type="image/png")
            tournesol_footer = Image.new("RGBA", (320, 60), (255, 200, 0, 255))
            tournesol_footer_draw = ImageDraw.Draw(tournesol_footer)

            truncated_title = entity.metadata.get("name", "")[:200]
            # TODO: optimize this with a dichotomic search
            while tournesol_footer_draw.textlength(truncated_title, font=fnt_title) > 300:
                truncated_title = truncated_title[:-4] + "..."
            tournesol_footer_draw.text(
                (10, 6), truncated_title, font=fnt_title, fill=(29, 26, 20, 255)
            )

            score = entity.tournesol_score
            if score is not None:
                tournesol_footer_draw.text(
                    (10, 25), "Tournesol Score: %.0f" % score, font=fnt, fill=(29, 26, 20, 255)
                )

            url = f"https://img.youtube.com/vi/{entity.video_id}/mqdefault.jpg"
            thumbnail_response = requests.get(url)
            if thumbnail_response.status_code != 200:
                logger.warning(
                    f"Fetching youtube thumbnail has non-200 status: {thumbnail_response.status_code}"
                )
                # Choosing not to raise an error here because the reponse often has a non-200
                # status while containing the right content (e.g. 304, 443)
                # raise ConnectionError
            youtube_thumbnail = Image.open(BytesIO(thumbnail_response.content)).convert("RGBA")

            # Merges the two images into one
            preview_image = Image.new("RGBA", (320, 240), (255, 255, 255, 0))
            preview_image.paste(youtube_thumbnail)
            preview_image.paste(tournesol_footer, box=(0, 180))
            preview_image.save(response, 'png')
            return response
        except Entity.DoesNotExist as e:
            # Probably: The entity does not exist on Tournesol
            logger.error(f"Error Caught: {e}")
            return DynamicWebsitePreviewDefault.default_preview()
        except AttributeError as e:
            # Probably: The entity is not a viedo and does not have a field `video_id`
            logger.error(f"Error Caught: {e}")
            return DynamicWebsitePreviewDefault.default_preview()
        except ConnectionError as e:
            # Probably: The thumbnail could not be fetched from youtube
            logger.error(f"Error Caught: {e}")
            return DynamicWebsitePreviewDefault.default_preview()
