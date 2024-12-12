from unittest.mock import patch

from django.test import Client, TestCase

from tournesol.tests.factories.entity import VideoFactory


def mock_get_static_index_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <title>Tournesol</title>
            <!--DJANGO_META_TAGS-->
        </head>
        <body>
            <h1>Mocked html page</h1>
        </body>
    </html>
    """


@patch("ssr.views.get_static_index_html", new=mock_get_static_index_html)
class RenderedHtmlTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_html_root(self):
        response = self.client.get("/ssr/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta property="og:title" content="Tournesol">')

    def test_index_html_arbitrary_path(self):
        response = self.client.get("/ssr/faq")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta property="og:title" content="Tournesol">')

    def test_index_html_video_entity(self):
        video = VideoFactory()

        response = self.client.get(f"/ssr/entities/{video.uid}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, f'<meta property="og:title" content="{video.metadata["name"]}">'
        )
        self.assertContains(response, '<meta property="og:type" content="video">')
