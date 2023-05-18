from rest_framework.renderers import BaseRenderer


class ImageRenderer(BaseRenderer):
    media_type = "image/*"
    format = ""
    render_style = "binary"
