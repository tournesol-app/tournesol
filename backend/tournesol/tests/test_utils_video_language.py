from django.test import TestCase

from tournesol.tests.factories.entity import VideoFactory
from tournesol.utils.video_language import compute_video_language


class VideoLanguageUtilsTestCase(TestCase):
    def test_language_detection(self):
        VideoFactory.create_batch(5, metadata__uploader="Tournesol4All", metadata__language="fr")
        VideoFactory.create_batch(2, metadata__uploader="Sunflower4All", metadata__language="en")
        test_details = [
            # [WHEN] the channel has more than 4 videos
            # [THEN] the language is inferred from the existing videos.
            (["Tournesol4All", "I speak english", "I have not description"], "fr"),
            # [WHEN] the channel has less than 4 videos
            # [THEN] the language is inferred from the given metadata.
            (["Sunflower4All", "I speak english", "I have not description"], "en"),
            (["Sunflower4All", "Je parle Français", "Bonjour, Merci beaucoup"], "fr"),
            (["Sunflower4All", "Ich spreche Deutsch", "Hallo, Danke schön"], "de"),
        ]

        for input_, output in test_details:
            self.assertEqual(compute_video_language(*input_), output)
