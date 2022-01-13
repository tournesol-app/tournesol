from datetime import date, timedelta
from unittest.mock import patch

from django.db.models import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from tournesol.utils.video_language import compute_video_language
from tournesol.tests.factories.video import VideoFactory, VideoCriteriaScoreFactory
from ..models import Tag, Video


class VideoApi(TestCase):
    """
    TestCase of the video API.
    """

    _user = "username"

    _list_of_videos = []

    def setUp(self):
        User.objects.create(username=self._user, email="user@test")

        self.video_1 = VideoFactory(
            publication_date=date(2021, 1, 1),
            uploader="uploader1",
        )
        self.video_2 = VideoFactory(
            publication_date=date(2021, 1, 2),
            uploader="uploader2",
        )
        self.video_3 = VideoFactory(
            publication_date=date(2021, 1, 3),
            uploader="uploader2",
        )
        self.video_4 = VideoFactory(
            publication_date=date(2021, 1, 4),
            uploader="uploader3",
        )
        self._list_of_videos = [self.video_1, self.video_2, self.video_3, self.video_4]
        VideoCriteriaScoreFactory(video=self.video_1, criteria="reliability", score=0.1)
        VideoCriteriaScoreFactory(video=self.video_2, criteria="reliability", score=0.2)
        VideoCriteriaScoreFactory(video=self.video_3, criteria="importance", score=0.3)
        VideoCriteriaScoreFactory(video=self.video_4, criteria="importance", score=0.4)

    def test_anonymous_can_list(self):
        """
        An anonymous user can list all videos.
        """
        client = APIClient()

        # test a request without query parameters
        response = client.get(
            reverse("tournesol:video-list"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_video_ids = [video["video_id"] for video in response.data["results"]]
        existing_video_ids = [video.video_id for video in self._list_of_videos]

        self.assertEqual(set(returned_video_ids), set(existing_video_ids))
        self.assertEqual(response.data["count"], len(self._list_of_videos))

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
            reverse("tournesol:video-list"),
            {"limit": limit},
            format="json",
        )
        returned_video_ids = [video["video_id"] for video in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(set(returned_video_ids).issubset(set(existing_video_ids)))
        self.assertEqual(response.data["count"], len(self._list_of_videos))
        self.assertEqual(len(response.data["results"]), limit)

        # test that a huge limit doesn't break anything
        limit = 10000
        response = client.get(
            reverse("tournesol:video-list"),
            {"limit": limit},
            format="json",
        )
        returned_video_ids = [video["video_id"] for video in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(returned_video_ids), set(existing_video_ids))
        self.assertEqual(response.data["count"], len(self._list_of_videos))
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
            reverse("tournesol:video-list"),
            {"offset": offset},
            format="json",
        )
        returned_video_ids = [video["video_id"] for video in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(set(returned_video_ids).issubset(set(existing_video_ids)))
        self.assertEqual(response.data["count"], len(self._list_of_videos))
        self.assertEqual(
            len(response.data["results"]), len(self._list_of_videos) - offset
        )

        # test that a huge offset doesn't break anything
        offset = 10000
        response = client.get(
            reverse("tournesol:video-list"),
            {"offset": offset},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(self._list_of_videos))
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
            {"limit": 1, "offset": videos_in_db - 2},
            # the limit exceeds the number of videos, not the offset
            {"limit": videos_in_db * 2, "offset": videos_in_db - 2},
            # the limit exceeds the number of videos, so does the offset
            {"limit": videos_in_db * 2, "offset": videos_in_db + 1},
        ]

        for param in parameters:
            response = client.get(
                reverse("tournesol:video-list"),
                {"limit": param["limit"], "offset": param["offset"]},
                format="json",
            )
            returned_video_ids = [
                video["video_id"] for video in response.data["results"]
            ]

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(set(returned_video_ids).issubset(set(existing_video_ids)))

            if param["limit"] <= videos_in_db - param["offset"]:
                self.assertEqual(len(response.data["results"]), param["limit"])

            else:
                if param["offset"] >= videos_in_db:
                    self.assertEqual(len(response.data["results"]), 0)
                else:
                    self.assertEqual(
                        len(response.data["results"]), videos_in_db - param["offset"]
                    )

    def test_list_videos_with_criteria_weights(self):
        client = APIClient()

        # Default weights: all criterias contribute equally
        resp = client.get("/video/")
        self.assertEqual(
            [r["video_id"] for r in resp.json()["results"]],
            [self.video_4.video_id, self.video_3.video_id, self.video_2.video_id, self.video_1.video_id],
        )

        # Disable reliability
        resp = client.get("/video/?reliability=0")
        self.assertEqual(
            [r["video_id"] for r in resp.json()["results"]],
            [self.video_4.video_id, self.video_3.video_id],
        )

        # Disable both reliability and importance
        resp = client.get("/video/?reliability=0&importance=0")
        self.assertEqual([r["video_id"] for r in resp.json()["results"]], [])

        # More weight to reliability should change the order
        resp = client.get("/video/?reliability=100&importance=10")
        self.assertEqual(
            [r["video_id"] for r in resp.json()["results"]],
            [self.video_2.video_id, self.video_1.video_id, self.video_4.video_id, self.video_3.video_id],
        )

    def test_anonymous_can_get_video(self):
        client = APIClient()
        response = client.get(f"/video/{self.video_1.video_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["video_id"], self.video_1.video_id)

    def test_anonymous_can_get_video_with_score_zero(self):
        # The default filter used to fetch a list should not be applied to retrieve a single video
        client = APIClient()
        VideoFactory(video_id="vid_score_0")
        response = client.get("/video/vid_score_0/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["video_id"], "vid_score_0")

    def test_anonymous_cant_get_video_non_existing(self):
        client = APIClient()
        response = client.get("/video/video_id_00/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_language_detection(self):
        VideoFactory.create_batch(5, uploader="Tournesol4All", language="fr")
        # Not enough videos to qualify for skipping language detection
        VideoFactory.create_batch(2, uploader="Sunflower4All", language="en")
        test_details = [
            (
                ["Tournesol4All", "I speak english", "I have not description"],
                "fr",
            ),  # fr because of existing known channel
            (["Sunflower4All", "I speak english", "I have not description"], "en"),
            (["Sunflower4All", "Je parle Français", "Bonjour, Merci beaucoup"], "fr"),
            (["Sunflower4All", "Ich spreche Deutsch", "Hallo, Danke schön"], "de"),
        ]
        for input_, output in test_details:
            self.assertEqual(compute_video_language(*input_), output)

    def test_cannot_get_existing_video_without_positive_score(self):
        client = APIClient()
        VideoFactory(video_id='video_null_score')
        response = client.get("/video/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(self._list_of_videos))

    def test_cannot_get_video_with_particular_request(self):
        client = APIClient()
        video = VideoFactory()
        VideoCriteriaScoreFactory(video=video, criteria="engaging", score=-1)
        VideoCriteriaScoreFactory(video=video, criteria="importance", score=1)
        good_response = client.get("/video/?importance=50&engaging=0")
        self.assertEqual(good_response.status_code, status.HTTP_200_OK)
        self.assertEqual(good_response.data["count"], len(self._list_of_videos) + 1)
        bad_response = client.get("/video/?importance=50&engaging=100")
        self.assertEqual(bad_response.status_code, status.HTTP_200_OK)
        self.assertEqual(bad_response.data["count"], len(self._list_of_videos))

    def test_get_video_languages_filter(self):
        client = APIClient()

        # Add 1 video in French and 2 videos in English
        video1 = VideoFactory(language="fr")
        video2 = VideoFactory(language="en")
        video3 = VideoFactory(language="en")
        VideoCriteriaScoreFactory(video=video1)
        VideoCriteriaScoreFactory(video=video2)
        VideoCriteriaScoreFactory(video=video3)

        resp = client.get("/video/?language=")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # not filtered, 3 videos were added
        self.assertEqual(resp.data["count"], len(self._list_of_videos) + 3)

        resp = client.get("/video/?language=fr")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)  # 1 French video

        resp = client.get("/video/?language=de,en,fr")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 3)  # 1 French and 2 English videos

    def test_get_video_date_filters(self):
        client = APIClient()

        resp = client.get("/video/?date_gte=2021-01-04T00:00:00")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["count"], 1)

        resp = client.get("/video/?date_lte=2021-01-03T00:00:00")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 3)

    def test_get_video_date_filters_legacy_format(self):
        client = APIClient()

        resp = client.get("/video/?date_gte=04-01-21-00-00-00")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

        resp = client.get("/video/?date_lte=03-01-21-00-00-00")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 3)

    def test_search_in_tags_should_not_affect_order(self):
        self.video_1.tags.create(name="tag1")
        self.video_1.tags.create(name="tag2")
        self.video_1.tags.create(name="tag3")
        self.video_2.tags.create(name="tag4")

        client = APIClient()
        resp = client.get("/video/?search=tag")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), 2)
        # Video2 with higher score should remain listed as the top video
        self.assertEqual(resp.data["results"][0]["video_id"], self.video_2.video_id)

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
        initial_video_nbr = Video.objects.all().count()

        client.force_authenticate(user=user)

        response = client.post("/video/", {"video_id": "NeADlWSDFAQ"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Video.objects.all().count(), initial_video_nbr + 1)

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

        VideoFactory(video_id=new_video_id)

        response = client.post("/video/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        video = Video.objects.filter(video_id=new_video_id)
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
            Video.objects.get(video_id=id_too_big)

        response = client.post("/video/", {"video_id": id_too_small}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with self.assertRaises(ObjectDoesNotExist):
            Video.objects.get(video_id=id_too_small)

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
                        "description": "Video description",
                        "liveBroadcastContent": "none",
                        "localized": {},
                        "publishedAt": "2012-10-01T15:27:35Z",
                        "tags": ["tournesol"],
                        "thumbnails": {},
                        "title": "Video title",
                    },
                    "statistics": {
                        "commentCount": "8887",
                        "dislikeCount": "5773",
                        "favoriteCount": "0",
                        "likeCount": "307433",
                        "viewCount": "20186268",
                    },
                }
            ],
            "kind": "youtube#videoListResponse",
            "pageInfo": {"resultsPerPage": 1, "totalResults": 1},
        }

        client = APIClient()

        user = User.objects.get(username=self._user)
        initial_video_nbr = Video.objects.all().count()

        new_video_id = "NeADlWSDFAQ"
        data = {"video_id": new_video_id}

        client.force_authenticate(user=user)

        response = client.post("/video/", data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(Video.objects.all().count(), initial_video_nbr + 1)

        video = Video.objects.get(video_id=new_video_id)
        tournesol_tag = Tag.objects.get(name="tournesol")

        self.assertEqual(response.json()["name"], "Video title")
        self.assertIn(tournesol_tag, video.tags.all())
        self.assertEqual(response.json()["duration"], 1263)
        self.assertEqual(video.duration, timedelta(minutes=21, seconds=3))

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
                        "description": "Video description",
                        "liveBroadcastContent": "none",
                        "localized": {},
                        "publishedAt": "2012-10-01T15:27:35Z",
                        "tags": ["tournesol"],
                        "thumbnails": {},
                        "title": "Video title",
                    },
                    "statistics": {},
                }
            ],
            "kind": "youtube#videoListResponse",
            "pageInfo": {"resultsPerPage": 1, "totalResults": 1},
        }

        client = APIClient()

        user = User.objects.get(username=self._user)
        initial_video_nbr = Video.objects.all().count()

        new_video_id = "NeADlWSDFAQ"
        data = {"video_id": new_video_id}

        client.force_authenticate(user=user)

        response = client.post("/video/", data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(Video.objects.all().count(), initial_video_nbr + 1)

        video = Video.objects.get(video_id=new_video_id)
        self.assertEqual(response.json()["name"], "Video title")
        self.assertEqual(video.views, None)

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
            Video.objects.get(video_id=new_video_id)

    def test_get_video_uploader(self):
        client = APIClient()
        resp = client.get("/video/?uploader=uploader2")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)

    def test_video_views_stored_on_64bits(self):
        Video.objects.filter(video_id=self.video_1.video_id).update(views=9_000_000_000)
        video = Video.objects.get(video_id=self.video_1.video_id)
        self.assertEqual(video.views, 9_000_000_000)
