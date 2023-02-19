import csv
import io
import re
import shutil
import zipfile
from collections import ChainMap
from pathlib import Path
from tempfile import gettempdir
from typing import Dict

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from core.tests.factories.user import UserFactory
from tournesol.models import (
    ComparisonCriteriaScore,
    ContributorRating,
    ContributorRatingCriteriaScore,
    EntityCriteriaScore,
    Poll,
)
from tournesol.tests.factories.comparison import ComparisonCriteriaScoreFactory, ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.entity_score import EntityCriteriaScoreFactory

export_test_override_settings = override_settings(
    MEDIA_ROOT=gettempdir(),
    APP_TOURNESOL=ChainMap(
        {"DATASETS_BUILD_DIR": "ts_api_test_datasets"}, settings.APP_TOURNESOL
    ),
)

class ExportTest(TestCase):
    def setUp(self) -> None:
        self.poll_videos = Poll.default_poll()
        self.user_with_comparisons = User.objects.create_user(
            username="user_with", email="user_with@example.com"
        )

        self.video1 = VideoFactory()
        self.video2 = VideoFactory()
        self.comparison = ComparisonFactory(
            user=self.user_with_comparisons,
            entity_1=self.video1,
            entity_2=self.video2,
        )
        ComparisonCriteriaScore.objects.create(
            comparison=self.comparison, score=5, criteria="largely_recommended"
        )
        self.user_without_comparisons = UserFactory(username="user_without_comparisons")

        self.user_with_public_comparisons = UserFactory(
            username="public_comparisons", trust_score=0.5844
        )
        self.video_public_1 = VideoFactory()
        self.video_public_2 = VideoFactory()
        self.video_private_3 = VideoFactory()
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=self.user_with_public_comparisons,
            entity=self.video_public_1,
            is_public=True,
        )
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=self.user_with_public_comparisons,
            entity=self.video_public_2,
            is_public=True,
        )
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=self.user_with_public_comparisons,
            entity=self.video_private_3,
            is_public=False,
        )
        self.comparison_public = ComparisonFactory(
            poll=self.poll_videos,
            user=self.user_with_public_comparisons,
            entity_1=self.video_public_1,
            entity_2=self.video_public_2,
        )
        ComparisonCriteriaScoreFactory(
            comparison=self.comparison_public, score=5, criteria="largely_recommended"
        )
        self.comparison_private = ComparisonFactory(
            user=self.user_with_public_comparisons,
            entity_1=self.video_public_1,
            entity_2=self.video_private_3,
        )
        ComparisonCriteriaScoreFactory(
            comparison=self.comparison_private, score=5, criteria="largely_recommended"
        )

        self.client = APIClient()
        cache.clear()

    def tearDown(self) -> None:
        """
        Delete the temporary directory created by the call to the mgmt command
        `create_dataset`.
        """
        try:
            shutil.rmtree(Path(gettempdir()).joinpath("ts_api_test_datasets"))
        except FileNotFoundError:
            pass

    def add_comparison(self, user, is_public=True):
        video1 = VideoFactory()
        video2 = VideoFactory()
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=user,
            entity=video1,
            is_public=is_public,
        )
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=user,
            entity=video2,
            is_public=is_public,
        )
        ComparisonFactory(
            poll=self.poll_videos,
            user=user,
            entity_1=video1,
            entity_2=video2,
        )

    def extract_export_root(self, response):
        content_disposition = response.headers["Content-Disposition"]
        match = re.search(
            "attachment; filename=(tournesol_dataset_\\d{8}).zip",
            content_disposition,
        )
        self.assertIsNotNone(match)
        root = match.group(1)
        return root

    def parse_zipped_csv(self, response: requests.models.Response, filename: str) -> Dict[str, str]:
        content_disposition = response.headers["Content-Disposition"]
        match = re.search("filename=(.+).zip", content_disposition)
        root = Path(match.group(1))
        zip_content = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_content, "r") as zip_file:
            with zip_file.open(str(root / filename), "r") as file:
                content = file.read().decode("utf-8")
                csv_file = csv.DictReader(io.StringIO(content))
                rows = list(csv_file)
        return rows

    def test_not_authenticated_cannot_download_comparisons(self):
        resp = self.client.get("/users/me/exports/comparisons/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_with_comparisons_can_download_comparisons(self):
        self.client.force_authenticate(self.user_with_comparisons)
        resp = self.client.get("/users/me/exports/comparisons/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Ensures that the csv contians a single row with the correct score
        csv_file = csv.DictReader(io.StringIO(resp.content.decode()))
        comparison_list = list(csv_file)
        self.assertEqual(len(comparison_list), 1)
        self.assertEqual(float(comparison_list[0]["score"]), 5.0)

    def test_authenticated_without_comparisons_can_download_comparisons(self):
        self.client.force_authenticate(self.user_without_comparisons)
        resp = self.client.get("/users/me/exports/comparisons/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Ensures the csv does not contain information about comparison criteria score
        csv_file = csv.DictReader(io.StringIO(resp.content.decode()))
        comparison_list = list(csv_file)
        self.assertEqual(len(comparison_list), 0)

    def test_not_authenticated_cannot_download_all(self):
        resp = self.client.get("/users/me/exports/all/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_with_comparisons_can_download_all(self):
        self.client.force_authenticate(self.user_with_comparisons)
        resp = self.client.get("/users/me/exports/all/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/zip")

    def test_authenticated_without_comparisons_can_download_all(self):
        self.client.force_authenticate(self.user_without_comparisons)
        resp = self.client.get("/users/me/exports/all/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/zip")

    def test_not_authenticated_can_download_public_comparisons(self):
        resp = self.client.get("/exports/comparisons/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Ensures the csv does not contain information that are not public comparisons
        csv_file = csv.DictReader(io.StringIO(resp.content.decode()))
        comparison_list = list(csv_file)
        self.assertEqual(len(comparison_list), 1)
        self.assertEqual(comparison_list[0]["video_a"], self.video_public_1.video_id)
        self.assertEqual(comparison_list[0]["video_b"], self.video_public_2.video_id)

    def test_not_authenticated_can_download_public_comparisons_multiple_users(self):
        self.public_comparisons2 = UserFactory()
        self.video_public_3 = VideoFactory()
        self.video_public_4 = VideoFactory()
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=self.public_comparisons2,
            entity=self.video_public_3,
            is_public=True,
        )
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=self.public_comparisons2,
            entity=self.video_public_4,
            is_public=True,
        )
        self.comparison_public2 = ComparisonFactory(
            user=self.public_comparisons2,
            entity_1=self.video_public_3,
            entity_2=self.video_public_4,
        )
        ComparisonCriteriaScoreFactory(
            comparison=self.comparison_public2, score=10, criteria="largely_recommended"
        )
        resp = self.client.get("/exports/comparisons/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Ensures the csv does not contain information that are not public comparisons
        csv_file = csv.DictReader(io.StringIO(resp.content.decode()))
        comparison_list = list(csv_file)
        self.assertEqual(len(comparison_list), 2)
        self.assertEqual(comparison_list[0]["video_a"], self.video_public_1.video_id)
        self.assertEqual(comparison_list[0]["video_b"], self.video_public_2.video_id)
        self.assertEqual(comparison_list[1]["video_a"], self.video_public_3.video_id)
        self.assertEqual(comparison_list[1]["video_b"], self.video_public_4.video_id)

    @export_test_override_settings
    def test_non_authenticated_can_fetch_export_all_200(self):
        call_command("create_dataset")
        response = self.client.get("/exports/all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "application/zip")

    @export_test_override_settings
    def test_public_dataset_contains_all_expected_files(self):
        call_command("create_dataset")
        response = self.client.get("/exports/all/")
        zip_content = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_content, "r") as zip_file:
            expected_filenames = [
                "README.txt",
                "users.csv",
                "comparisons.csv",
                "individual_criteria_scores.csv",
                "collective_criteria_scores.csv",
            ]
            filenames = [filepath.rsplit("/", 1)[-1] for filepath in zip_file.namelist()]
            self.assertEqual(filenames, expected_filenames)

    @export_test_override_settings
    def test_export_readme_equals_resources_readme(self):
        call_command("create_dataset")
        response = self.client.get("/exports/all/")
        root = self.extract_export_root(response)
        zip_content = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_content, "r") as zip_file:
            with zip_file.open(root + "/README.txt", "r") as file:
                content = file.read()
                with open("tournesol/resources/export_readme.txt", "rb") as readme_file:
                    expected_content = readme_file.read()
                self.assertEqual(content, expected_content)

    @export_test_override_settings
    def test_export_all_comparisons_equal_export_comparisons(self):
        call_command("create_dataset")
        response = self.client.get("/exports/all/")
        root = self.extract_export_root(response)
        zip_content = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_content, "r") as zip_file:
            with zip_file.open(root + "/comparisons.csv", "r") as file:
                expected_content = self.client.get("/exports/comparisons/").content
                self.assertEqual(file.read(), expected_content)

    @export_test_override_settings
    def test_users_with_public_comparisons_uniquely_added_to_users_export(self):
        # Make sure this user has multiple public comparisons so
        # that we can verify they are only added once in the CSV
        self.add_comparison(user=self.user_with_public_comparisons, is_public=True)
        call_command("create_dataset")
        response = self.client.get("/exports/all/")
        rows = self.parse_zipped_csv(response, "users.csv")
        usernames = set(row["public_username"] for row in rows)
        self.assertNotIn(self.user_with_comparisons.username, usernames)
        self.assertNotIn(self.user_without_comparisons.username, usernames)
        self.assertIn(self.user_with_public_comparisons.username, usernames)
        username = self.user_with_public_comparisons.username
        user_rows = [row for row in rows if row["public_username"] == username]
        self.assertEqual(len(user_rows), 1)
        user_row = user_rows[0]
        self.assertEqual(user_row["trust_score"], "0.5844")

    @export_test_override_settings
    def test_user_with_only_private_comparisons_not_in_users(self):
        user_with_only_private_comparisons = UserFactory(username="privacy_conscious")
        self.add_comparison(user=user_with_only_private_comparisons, is_public=False)
        self.add_comparison(user=user_with_only_private_comparisons, is_public=False)
        self.add_comparison(user=user_with_only_private_comparisons, is_public=False)
        call_command("create_dataset")
        response = self.client.get("/exports/all/")
        rows = self.parse_zipped_csv(response, "users.csv")
        usernames = set(row["public_username"] for row in rows)
        self.assertNotIn(user_with_only_private_comparisons.username, usernames)

    @export_test_override_settings
    def test_anon_cant_download_non_existing_dataset(self):
        """
        Anonymous and authenticated users cannot download a dataset when no
        dataset is available on the server.
        """
        # The dir "datasets" should not exist by default.
        datasets_dir = Path(gettempdir()).joinpath("ts_api_test_datasets")
        self.assertFalse(datasets_dir.exists())

        response = self.client.get("/exports/all/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.headers["Content-Type"], "application/json")

    @export_test_override_settings
    def test_all_exports_voting_rights(self):
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 0)

        last_user = UserFactory(username="z")
        first_user = UserFactory(username="a")

        self.add_comparison(user=last_user, is_public=True)
        self.add_comparison(user=first_user, is_public=True)
        self.add_comparison(user=first_user, is_public=True)
        self.add_comparison(user=first_user, is_public=False)

        last_user_public_contributor_ratings = ContributorRating.objects.filter(
            user=last_user,
            is_public=True,
        )
        first_user_public_contributor_ratings = ContributorRating.objects.filter(
            user=first_user,
            is_public=True,
        )
        first_user_private_contributor_ratings = ContributorRating.objects.filter(
            user=first_user,
            is_public=False,
        )

        # ContributorRatingCriteriaScore that should not be exported
        ContributorRatingCriteriaScore.objects.create(
            contributor_rating=first_user_private_contributor_ratings[0],
            criteria="criteria2",
            voting_right=0.4855,
            score=0.5214,
        )
        ContributorRatingCriteriaScore.objects.create(
            contributor_rating=first_user_private_contributor_ratings[1],
            criteria="criteria1",
            voting_right=0.4444,
            score=-5.5555,
        )

        # ContributorRatingCriteriaScore that should be exported
        expected_exports = [
            ContributorRatingCriteriaScore.objects.create(
                contributor_rating=first_user_public_contributor_ratings[2],
                criteria="criteria2",
                voting_right=0.1234,
                score=2.4567,
            ),
            ContributorRatingCriteriaScore.objects.create(
                contributor_rating=last_user_public_contributor_ratings[0],
                criteria="criteria2",
                voting_right=0.11,
                score=-0.66,
            ),
            ContributorRatingCriteriaScore.objects.create(
                contributor_rating=first_user_public_contributor_ratings[0],
                criteria="criteria1",
                voting_right=0.8,
                score=1.9,
            ),
        ]

        # Expect results sorted first by username then by video id and finally by criteria
        expected_exports = sorted(
            expected_exports, key=lambda x: (
            x.contributor_rating.user.username,
            x.contributor_rating.entity.metadata["video_id"],
            x.criteria
            )
        )

        call_command("create_dataset")
        response = self.client.get("/exports/all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "application/zip")
        rows = self.parse_zipped_csv(response, "individual_criteria_scores.csv")

        for expected_export, row in zip(expected_exports, rows):
            row = rows.pop(0)
            self.assertEqual(
                row["public_username"],
                expected_export.contributor_rating.user.username,
            )
            self.assertEqual(
                row["video"],
                expected_export.contributor_rating.entity.metadata["video_id"],
            )
            self.assertEqual(row["criteria"], expected_export.criteria)
            self.assertEqual(row["score"], str(expected_export.score))
            self.assertEqual(row["voting_right"], str(expected_export.voting_right))

    @export_test_override_settings
    def test_all_export_sorts_by_username(self):
        last_user = UserFactory(username="z")
        first_user = UserFactory(username="a")
        self.add_comparison(user=last_user, is_public=True)
        self.add_comparison(user=first_user, is_public=True)

        call_command("create_dataset")
        response = self.client.get("/exports/all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rows = self.parse_zipped_csv(response, "users.csv")
        usernames = [row["public_username"] for row in rows]
        self.assertEqual("a", usernames[0])
        self.assertEqual("z", usernames[-1])

    @export_test_override_settings
    def test_all_export_contains_collective_criteria_scores(self):
        EntityCriteriaScoreFactory(criteria="h2g2", score=42, entity__metadata__name="DON'T PANIC")
        call_command("create_dataset")
        response = self.client.get("/exports/all/")
        rows = self.parse_zipped_csv(response, "collective_criteria_scores.csv")
        self.assertEqual(len(rows), 1)
        self.assertEqual(float(rows[0]["score"]), 42.)
        self.assertEqual(rows[0]["criteria"], "h2g2")
        self.assertEqual(rows[0]["name"], "DON'T PANIC")

    @export_test_override_settings
    def test_collective_criteria_scores_is_empty_without_criteria_scores(self):
        EntityCriteriaScore.objects.all().delete
        call_command("create_dataset")
        response = self.client.get("/exports/all/")
        rows = self.parse_zipped_csv(response, "collective_criteria_scores.csv")
        self.assertEqual(len(rows), 0)
