from rest_framework.renderers import StaticHTMLRenderer


class ImageRenderer(StaticHTMLRenderer):
    media_type = "image/*"
    format = ""
    render_style = "binary"
