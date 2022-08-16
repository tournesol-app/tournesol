from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from django.http import HttpResponse, FileResponse
from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView

from tournesol.models.entity import Entity

POPPINS_FONT = ImageFont.truetype("tournesol/resources/Poppins-Medium.ttf", 20)


class DynamicWebsitePreviewDefault(APIView):
    permission_classes = []

    @extend_schema(
        description="Default website preview",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        default_preview = open("tournesol/resources/tournesol_screenshot_og.png", "rb")
        response = FileResponse(default_preview, content_type="image/png")
        return response

class DynamicWebsitePreviewEntity(APIView):
    permission_classes = []

    @extend_schema(
        description="Website preview for entities page",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, uid):
        # try:
        entity = Entity.objects.get(uid=uid)
        response = HttpResponse(content_type="image/png")
        tournesol_footer = Image.new("RGBA", (320, 60), (255, 200, 0, 255))
        tournesol_footer_draw = ImageDraw.Draw(tournesol_footer)
        title = entity.metadata.get("name", "")
        max_title_length = 38
        truncated_title = title if len(title) < max_title_length else title[:(max_title_length-3)] + "..."
        tournesol_footer_draw.text((10, 0), truncated_title, font=ImageFont.truetype("tournesol/resources/Poppins-Medium.ttf", 16), fill=(29, 26, 20, 255))

        score = entity.tournesol_score
        if score is not None:
            tournesol_footer_draw.text((10, 25), "Score: %.0f" % score, font=POPPINS_FONT, fill=(29, 26, 20, 255))
            tournesol_footer_draw.text((120, 25), "Contributors: %.0f" % entity.rating_n_contributors, font=POPPINS_FONT, fill=(29, 26, 20, 255))


        url=f"https://img.youtube.com/vi/{entity.video_id}/mqdefault.jpg"
        youtube_thumbnail = Image.open(BytesIO(requests.get(url).content)).convert("RGBA") 

        # Merges the two images into one
        preview_image = Image.new("RGBA", (320, 240), (255, 255, 255, 0))
        preview_image.paste(youtube_thumbnail)
        preview_image.paste(tournesol_footer, box=(0, 180))
        preview_image.save(response, 'png')
        return response
        # except:
        #     default_preview = open("tournesol/resources/tournesol_screenshot_og.png", "rb")
        #     return FileResponse(default_preview, content_type="image/png")
