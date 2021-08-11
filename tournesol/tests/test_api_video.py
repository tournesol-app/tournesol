from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from tournesol.models import Video


class VideoApi(TestCase):
    """
    TestCase of the Video API.

    """

    def test_upload_video(self):
        factory = APIClient()
        response = factory.post(
            "/video/",
            {'video_id':'AZERTYUIOPV'},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_video_already_exist(self):
        Video.objects.create(video_id="lsORjv-zerh")
        client = APIClient()
        data={'video_id':'lsORjv-zerh'}
        response = client.post(
            "/video/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_video_incorrect_id(self):
        factory = APIClient()
        response = factory.post(
            "/video/",
            {'video_id':'AZERTYUIOPV3'}, # length of 12
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = factory.post(
            "/video/",
            {'video_id':'AZERTYUPV3'}, # length of 10
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def get_existing_video(self):
        Video.objects.create(video_id='AZERTYUIOPV')
        factory = APIClient()
        response = factory.get(
            "/video/",
            {'video_id':'AZERTYUIOPV'},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def get_existing_video(self):
        factory = APIClient()
        response = factory.get(
            "/video/",
            {'video_id':'AZERTYUIOPV'},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)