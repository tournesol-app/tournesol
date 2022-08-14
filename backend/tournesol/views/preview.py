from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from django.http import HttpResponse, FileResponse
from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView

POPPINS_FONT = ImageFont.truetype("../frontend/public/fonts/Poppins-Bold.ttf", 40)


class DynamicWebsitePreview(APIView):
    permission_classes = []

    @extend_schema(
        description="preview the ",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        default_preview = open("../frontend/public/tournesol_screenshot_og.png", "rb")
        response = FileResponse(default_preview, content_type="image/png")
        return response

class DynamicWebsitePreviewEntity(APIView):
    permission_classes = []

    @extend_schema(
        description="Website preview for entities page",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, uid):
        response = HttpResponse(content_type="image/png")
        tournesol_footer = Image.new("RGBA", (320, 60), (255, 200, 0, 255))
        tournesol_footer_draw = ImageDraw.Draw(tournesol_footer)
        tournesol_footer_draw.text((10, 0), "by", font=POPPINS_FONT, fill=(29, 26, 20, 255))
        tournesol_footer_draw.text((80, 0), "Tournesol", font=POPPINS_FONT, fill=(29, 26, 20, 255))

        # TODO double check that this should be always 320x180.
        url=f"https://img.youtube.com/vi/{uid}/mqdefault.jpg"
        youtube_thumbnail = Image.open(BytesIO(requests.get(url).content)).convert("RGBA") 

        # Merges the two images into one
        preview_image = Image.new("RGBA", (320, 240), (255, 255, 255, 0))
        preview_image.paste(youtube_thumbnail)
        preview_image.paste(tournesol_footer, box=(0, 180))
        preview_image.save(response, 'png')
        return response
        