from unittest.mock import patch

from django.db.models import ObjectDoesNotExist
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from tournesol.entities.video import YOUTUBE_UID_NAMESPACE
from tournesol.tests.factories.entity import VideoCriteriaScoreFactory, VideoFactory
from tournesol.utils.video_language import compute_video_language

from ..models import Entity


class VideoApi(TestCase):
    """
    TestCase of the video API.
    """

    _user = "username"

    _list_of_videos = []

    def setUp(self):
        User.objects.create(username=self._user, email="user@test")

        self.video_1 = VideoFactory(
            metadata__publication_date="2021-01-01T19:44:24.686532",
            metadata__uploader="uploader1",
            tournesol_score=21.1,
        )
        self.video_2 = VideoFactory(
            metadata__publication_date="2021-01-02T19:44:24.686532",
            metadata__uploader="uploader2",
            tournesol_score=22.2,
        )
        self.video_3 = VideoFactory(
            metadata__publication_date="2021-01-03T19:44:24.686532",
            metadata__uploader="uploader2",
            tournesol_score=23.3,
        )
        self.video_4 = VideoFactory(
            metadata__publication_date="2021-01-04T19:44:24.686532",
            metadata__uploader="uploader3",
            tournesol_score=24.4,
        )
        self._list_of_videos = [self.video_1, self.video_2, self.video_3, self.video_4]
        VideoCriteriaScoreFactory(
            entity=self.video_1, criteria="reliability", score=0.1
        )
        VideoCriteriaScoreFactory(
            entity=self.video_2, criteria="reliability", score=0.2
        )
        VideoCriteriaScoreFactory(entity=self.video_3, criteria="importance", score=0.3)
        VideoCriteriaScoreFactory(entity=self.video_4, criteria="importance", score=0.4)

    def test_anonymous_cant_create(self):
        """
        An anonymous user can't add a new video.
        """
        client = APIClient()
        response = client.post("/video/", {"video_id": "NeADlWSDFAQ"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_create_without_yt_api_key(self):
        """
        An authenticated user can add a new video, even without a YouTube API
        key configured.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        initial_video_nbr = Entity.objects.all().count()

        client.force_authenticate(user=user)

        response = client.post("/video/", {"video_id": "NeADlWSDFAQ"}, format="json")
        new_video = Entity.get_from_video_id(video_id="NeADlWSDFAQ")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Entity.objects.all().count(), initial_video_nbr + 1)

        # ensure newly created entities are considered videos from YT
        self.assertEqual(
            new_video.uid, "{}:{}".format(YOUTUBE_UID_NAMESPACE, "NeADlWSDFAQ")
        )
        self.assertEqual(new_video.type, "video")

    def test_authenticated_cant_create_twice(self):
        """
        An authenticated user can't add more than one video with the same video
        id.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        new_video_id = "NeADlWSDFAQ"
        data = {"video_id": new_video_id}

        client.force_authenticate(user=user)

        VideoFactory(metadata__video_id=new_video_id)

        response = client.post("/video/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        video = Entity.objects.filter(metadata__video_id=new_video_id)
        self.assertEqual(video.count(), 1)

    def test_authenticated_cant_create_with_incorrect_id(self):
        """
        An authenticated user can't add a video with an invalid video id.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        id_too_big = "AZERTYUIOPQS"
        id_too_small = "AZERTYUIOP"

        client.force_authenticate(user=user)

        response = client.post("/video/", {"video_id": id_too_big}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with self.assertRaises(ObjectDoesNotExist):
            Entity.get_from_video_id(video_id=id_too_big)

        response = client.post("/video/", {"video_id": id_too_small}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with self.assertRaises(ObjectDoesNotExist):
            Entity.get_from_video_id(video_id=id_too_small)

    @patch("tournesol.utils.api_youtube.get_youtube_video_details")
    def test_authenticated_can_create_with_yt_api_key(self, mock_youtube):
        """
        An authenticated user can add a new video, with a YouTube API key
        configured.
        """
        mock_youtube.return_value = {
            "items": [
                {
                    "contentDetails": {
                        "caption": "true",
                        "contentRating": {},
                        "definition": "hd",
                        "dimension": "2d",
                        "duration": "PT21M3S",
                        "licensedContent": True,
                        "projection": "rectangular",
                    },
                    "etag": "ntdShdXlk7wT8kjjPpNj9jwgyH4",
                    "id": "NeADlWSDFAQ",
                    "kind": "youtube#video",
                    "snippet": {
                        "categoryId": "22",
                        "channelId": "UCAuUUnT6oDeKwE6v1NGQxug",
                        "channelTitle": "TED",
                        "defaultAudioLanguage": "en",
                        "defaultLanguage": "en",
                        "description": "Entity description",
                        "liveBroadcastContent": "none",
                        "localized": {},
                        "publishedAt": "2012-10-01T15:27:35Z",
                        "tags": ["tournesol"],
                        "thumbnails": {},
                        "title": "Entity title",
                    },
                    "statistics": {
                        "commentCount": "8887",
                        "dislikeCount": "5773",
                        "favoriteCount": "0",
                        "likeCount": "307433",
                        "viewCount": "20186268",
                    },
                    "status": {
                        "uploadStatus": "processed",
                        "privacyStatus": "public",
                        "license": "youtube",
                        "embeddable": True,
                        "publicStatsViewable": True,
                        "madeForKids": False,
                    },
                }
            ],
            "kind": "youtube#videoListResponse",
            "pageInfo": {"resultsPerPage": 1, "totalResults": 1},
        }

        client = APIClient()

        user = User.objects.get(username=self._user)
        initial_video_nbr = Entity.objects.all().count()

        new_video_id = "NeADlWSDFAQ"
        data = {"video_id": new_video_id}

        client.force_authenticate(user=user)

        response = client.post("/video/", data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(Entity.objects.all().count(), initial_video_nbr + 1)

        video = Entity.get_from_video_id(video_id=new_video_id)
        self.assertEqual(response.json()["name"], "Entity title")
        self.assertIn("tournesol", video.metadata["tags"])
        self.assertEqual(response.json()["duration"], 1263)
        self.assertEqual(video.metadata["duration"], 1263)

    @patch("tournesol.utils.api_youtube.get_youtube_video_details")
    def test_authenticated_can_create_with_yt_no_statistics(self, mock_youtube):
        """
        An authenticated user can add a new video, even if the YouTube API
        does not return its statistics.
        """
        mock_youtube.return_value = {
            "items": [
                {
                    "contentDetails": {
                        "caption": "true",
                        "contentRating": {},
                        "definition": "hd",
                        "dimension": "2d",
                        "duration": "PT21M3S",
                        "licensedContent": True,
                        "projection": "rectangular",
                    },
                    "etag": "ntdShdXlk7wT8kjjPpNj9jwgyH4",
                    "id": "NeADlWSDFAQ",
                    "kind": "youtube#video",
                    "snippet": {
                        "categoryId": "22",
                        "channelId": "UCAuUUnT6oDeKwE6v1NGQxug",
                        "channelTitle": "TED",
                        "defaultAudioLanguage": "en",
                        "defaultLanguage": "en",
                        "description": "Entity description",
                        "liveBroadcastContent": "none",
                        "localized": {},
                        "publishedAt": "2012-10-01T15:27:35Z",
                        "tags": ["tournesol"],
                        "thumbnails": {},
                        "title": "Entity title",
                    },
                    "statistics": {},
                    "status": {},
                }
            ],
            "kind": "youtube#videoListResponse",
            "pageInfo": {"resultsPerPage": 1, "totalResults": 1},
        }

        client = APIClient()

        user = User.objects.get(username=self._user)
        initial_video_nbr = Entity.objects.all().count()

        new_video_id = "NeADlWSDFAQ"
        data = {"video_id": new_video_id}

        client.force_authenticate(user=user)

        response = client.post("/video/", data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(Entity.objects.all().count(), initial_video_nbr + 1)

        video = Entity.get_from_video_id(video_id=new_video_id)
        self.assertEqual(response.json()["name"], "Entity title")
        self.assertEqual(video.metadata["views"], None)

    @patch("tournesol.utils.api_youtube.get_youtube_video_details")
    def test_authenticated_cant_create_with_yt_no_result(self, mock_youtube):
        """
        An authenticated user can't add a new video, if the YouTube API
        answers with an empty list.
        """
        mock_youtube.return_value = {
            "items": [],
            "kind": "youtube#videoListResponse",
            "pageInfo": {"resultsPerPage": 0, "totalResults": 0},
        }
        client = APIClient()

        user = User.objects.get(username=self._user)
        new_video_id = "NeADlWSDFAQ"
        data = {"video_id": new_video_id}

        client.force_authenticate(user=user)

        response = client.post("/video/", data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        with self.assertRaises(ObjectDoesNotExist):
            Entity.get_from_video_id(video_id=new_video_id)
