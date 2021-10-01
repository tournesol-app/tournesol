from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from tournesol.utils.video_language import compute_video_language

from ..models import Video, VideoCriteriaScore


class VideoApi(TestCase):
    """
    TestCase of the video API.
    """

    _video_id_01 = "video_id_01"
    _video_id_02 = "video_id_02"
    _video_id_03 = "video_id_03"
    _video_id_04 = "video_id_04"
    _list_of_videos = []

    def setUp(self):
        
        video_1 = Video.objects.create(video_id=self._video_id_01, name=self._video_id_01)
        video_2 = Video.objects.create(video_id=self._video_id_02, name=self._video_id_02)
        video_3 = Video.objects.create(video_id=self._video_id_03, name=self._video_id_03)
        video_4 = Video.objects.create(video_id=self._video_id_04, name=self._video_id_04)
        self._list_of_videos = [video_1, video_2, video_3, video_4]
        VideoCriteriaScore.objects.create(video=video_1, criteria="reliability", score=1)
        VideoCriteriaScore.objects.create(video=video_2, criteria="reliability", score=1)
        VideoCriteriaScore.objects.create(video=video_3, criteria="reliability", score=1)
        VideoCriteriaScore.objects.create(video=video_4, criteria="reliability", score=1)

    def test_anonymous_can_list(self):
        """
        An anonymous user can list all videos.
        """
        client = APIClient()

        # test a request without query parameters
        response = client.get(
            reverse("tournesol:video-list"), format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_video_ids = [video["video_id"] for video in response.data["results"]]
        existing_video_ids = [video.video_id for video in self._list_of_videos]

        self.assertEqual(set(returned_video_ids), set(existing_video_ids))
        self.assertEqual(response.data["count"], str(len(self._list_of_videos)))

    def test_anonymous_can_list_with_limit(self):
        """
        An anonymous user can list a subset of videos by using the `limit`
        query parameter.
        """
        client = APIClient()
        existing_video_ids = [video.video_id for video in self._list_of_videos]

        # test a request with the limit query parameter
        limit = 2
        response = client.get(
            reverse("tournesol:video-list"), {"limit": limit}, format="json",
        )
        returned_video_ids = [video["video_id"] for video in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(set(returned_video_ids).issubset(set(existing_video_ids)))
        self.assertEqual(response.data["count"], str(len(self._list_of_videos)))
        self.assertEqual(len(response.data["results"]), limit)

        # test that a huge limit doesn't break anything
        limit = 10000
        response = client.get(
            reverse("tournesol:video-list"), {"limit": limit}, format="json",
        )
        returned_video_ids = [video["video_id"] for video in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(returned_video_ids), set(existing_video_ids))
        self.assertEqual(response.data["count"], str(len(self._list_of_videos)))
        self.assertEqual(len(response.data["results"]), len(self._list_of_videos))

    def test_anonymous_can_list_with_offset(self):
        """
        An anonymous user can list a subset of videos by using the `offset`
        query parameter.
        """
        client = APIClient()
        existing_video_ids = [video.video_id for video in self._list_of_videos]

        offset = 2
        response = client.get(
            reverse("tournesol:video-list"), {"offset": offset}, format="json",
        )
        returned_video_ids = [video["video_id"] for video in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(set(returned_video_ids).issubset(set(existing_video_ids)))
        self.assertEqual(response.data["count"], str(len(self._list_of_videos)))
        self.assertEqual(len(response.data["results"]), len(self._list_of_videos) - offset)

        # test that a huge offset doesn't break anything
        offset = 10000
        response = client.get(
            reverse("tournesol:video-list"), {"offset": offset}, format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], str(len(self._list_of_videos)))
        self.assertEqual(len(response.data["results"]), 0)

    def test_anonymous_can_list_with_pagination(self):
        """
        An anonymous user can list a subset of videos by using all pagination
        parameters.

        Several combinations of parameters are checked, with coherent and
        incoherent values.
        """
        client = APIClient()
        existing_video_ids = [video.video_id for video in self._list_of_videos]
        videos_in_db = len(existing_video_ids)

        parameters = [
            # no parameters exceed the number of videos
            {"limit": 1, "offset":  videos_in_db - 2},
            # the limit exceeds the number of videos, not the offset
            {"limit": videos_in_db * 2, "offset": videos_in_db - 2},
            # the limit exceeds the number of videos, so does the offset
            {"limit": videos_in_db * 2, "offset": videos_in_db + 1}
        ]

        for param in parameters:
            response = client.get(
                reverse("tournesol:video-list"), {
                    "limit": param["limit"], "offset": param["offset"]
                }, format="json",
            )
            returned_video_ids = [video["video_id"] for video in response.data["results"]]

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(set(returned_video_ids).issubset(set(existing_video_ids)))

            if param["limit"] <= videos_in_db - param["offset"]:
                self.assertEqual(len(response.data["results"]), param["limit"])

            else:
                if param["offset"] >= videos_in_db:
                    self.assertEqual(len(response.data["results"]), 0)
                else:
                    self.assertEqual(len(response.data["results"]),
                                     videos_in_db - param["offset"])

    def test_upload_video_without_API_key(self):
        factory = APIClient()
        response = factory.post(
            "/video/",
            {'video_id':'NeADlWSDFAQ'},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("tournesol.views.video.youtube_video_details")
    def test_create_video_with_youtube_api(self, mock_youtube):
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
                        "projection": "rectangular"
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
                        "description": "Video description",
                        "liveBroadcastContent": "none",
                        "localized": {},
                        "publishedAt": "2012-10-01T15:27:35Z",
                        "tags": [],
                        "thumbnails": {},
                        "title": "Video title"
                    },
                    "statistics": {
                        "commentCount": "8887",
                        "dislikeCount": "5773",
                        "favoriteCount": "0",
                        "likeCount": "307433",
                        "viewCount": "20186268"
                    }
                }
            ],
            "kind": "youtube#videoListResponse",
            "pageInfo": {
                "resultsPerPage": 1,
                "totalResults": 1
            }
        }

        client = APIClient()
        response = client.post(
            "/video/",
            data={"video_id": "NeADlWSDFAQ"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(response.json()["name"], "Video title")

    @patch("tournesol.views.video.youtube_video_details")
    def test_create_video_with_with_youtube_api_no_result(self, mock_youtube):
        mock_youtube.return_value = {
            "items": [],
            "kind": "youtube#videoListResponse",
            "pageInfo": {
                "resultsPerPage": 0,
                "totalResults": 0
            }
        }

        client = APIClient()
        response = client.post(
            "/video/",
            data={"video_id": "NeADlWSDFAQ"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_upload_video_already_exist_without_API_key(self):
        Video.objects.create(video_id="NeADlWSDFAQ")
        client = APIClient()
        data={'video_id':'NeADlWSDFAQ'}
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
    
    def test_get_existing_video(self):
        factory = APIClient()
        response = factory.get("/video/video_id_01/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["video_id"], 'video_id_01')
    
    def test_get_non_existing_video(self):
        factory = APIClient()
        response = factory.get("/video/video_id_00/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_language_detection(self):
        Video.objects.create(uploader="Tournesol4All", language="fr", video_id="youtube1233")
        Video.objects.create(uploader="Tournesol4All", language="fr", video_id="youtube1234")
        Video.objects.create(uploader="Tournesol4All", language="fr", video_id="youtube1235")
        Video.objects.create(uploader="Tournesol4All", language="fr", video_id="youtube1236")
        Video.objects.create(uploader="Tournesol4All", language="fr", video_id="youtube1237")
        # Not enough videos to qualify for skipping language detection
        Video.objects.create(uploader="Sunflower4All", language="en", video_id="youtube1238")
        Video.objects.create(uploader="Sunflower4All", language="en", video_id="youtube1239")
        test_details = [
            (["Tournesol4All", "I speak english", "I have not description"], "fr"), # fr because of existing known channel
            (["Sunflower4All", "I speak english", "I have not description"], "en"),
            (["Sunflower4All", "Je parle Français", "Bonjour, Merci beaucoup"], "fr"),
            (["Sunflower4All", "Ich spreche Deutsch", "Hallo, Danke schön"], "de"),
        ]
        for input, output in test_details:
            self.assertEqual(compute_video_language(*input), output)

    def test_cannot_get_existing_video_without_positive_score(self):
        factory = APIClient()
        video_null_score = 'video_null_score'
        Video.objects.create(video_id=video_null_score)
        response = factory.get("/video/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], str(len(self._list_of_videos)))
