from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory


class UserSettingsDetailTestCase(TestCase):
    _username = "username"

    def setUp(self):
        self.client = APIClient()
        self.settings_base_url = "/users/me/settings/"

        self.user = UserFactory(username=self._username)
        self.valid_settings = {
            "videos": {
                "comparison__criteria_order": ["reliability"],
                "rate_later__auto_remove": 16,
                "recommendation__default_languages": ["en"],
                "recommendation__default_date": "Week",
                "recommendation__default_unsafe": False,
            }
        }

    def test_anon_401_get(self):
        """An anonymous user cannot get its own settings."""
        response = self.client.get(self.settings_base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_200_get(self):
        """An authenticated user can get its own settings."""
        self.client.force_authenticate(self.user)

        # When the user doesn't have any setting, the API should return an
        # empty dictionary.
        response = self.client.get(self.settings_base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {})

        # When the user have settings, the API should return them.
        new_settings = {
            "general": {
                "notifications__lang": "en",
                "notifications_email__research": True,
                "notifications_email__new_features": False,
            },
            "videos": {
                "comparison__auto_select_entities": True,
                "comparison__criteria_order": ["reliability"],
                "comparison_ui__weekly_collective_goal_display": "WEBSITE_ONLY",
                "comparison_ui__weekly_collective_goal_mobile": True,
                "extension__search_reco": True,
                "rate_later__auto_remove": 99,
                "recommendations__default_languages": ["en"],
                "recommendations__default_date": "WEEK",
                "recommendations__default_exclude_compared_entities": False,
                "recommendations__default_unsafe": False,
            },
        }
        self.user.settings = new_settings
        self.user.save(update_fields=["settings"])
        response = self.client.get(self.settings_base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, new_settings)

    def test_anon_401_put(self):
        """An anonymous user cannot replace all its settings."""
        response = self.client.put(self.settings_base_url, data=self.valid_settings, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_200_put(self):
        """An authenticated user can replace all its settings."""
        self.client.force_authenticate(self.user)

        # [GIVEN] An initial set of settings, containing two scopes with extra
        # keys.
        initial_settings = {
            "general": {"notifications_email__research": True},
            "videos": {"rate_later__auto_remove": 4, "extra_key": 99},
            "presidentielle2022": {"rate_later__auto_remove": 4, "extra_key": 99},
        }
        self.user.settings = initial_settings
        self.user.save(update_fields=["settings"])

        # [WHEN] The user replace its settings by new ones containing only one
        # scope and no extra key.
        new_settings = {"videos": {"rate_later__auto_remove": 99}}
        response = self.client.put(self.settings_base_url, data=new_settings, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # [THEN] The new settings should completely replace the previous ones.
        # Only the provided scope should remain with no extra key.
        self.assertDictEqual(response.data, new_settings)
        self.user.refresh_from_db()
        self.assertDictEqual(self.user.settings, new_settings)

    def test_anon_401_patch(self):
        """An anonymous user cannot update a subset of its settings."""
        response = self.client.patch(
            self.settings_base_url, data=self.valid_settings, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_200_patch(self):
        """An authenticated user can update a subset of its settings."""
        self.client.force_authenticate(self.user)

        # [GIVEN] An initial set of settings, containing two scopes with extra
        # keys.
        initial_settings = {
            "videos": {"rate_later__auto_remove": 4, "extra_key": 99},
            "presidentielle2022": {"rate_later__auto_remove": 4, "extra_key": 99},
        }
        self.user.settings = initial_settings
        self.user.save(update_fields=["settings"])

        # [WHEN] The user updates its settings by new ones containing only one
        # scope and no extre key.
        new_settings = {"videos": {"rate_later__auto_remove": 99}}
        response = self.client.patch(self.settings_base_url, data=new_settings, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        merged_settings = initial_settings.copy()
        merged_settings["videos"].update(new_settings["videos"])

        # [THEN] Only the provided keys of the provided scope should be
        # updated.

        # The API return the settings according ot its serializer...
        self.assertDictEqual(
            response.data,
            {"videos": {"rate_later__auto_remove": 99}},
        )
        # ... but the database contains all saved settings.
        self.user.refresh_from_db()
        self.assertDictEqual(self.user.settings, merged_settings)

    def test_auth_400_patch_invalid_setting(self):
        """
        An authenticated user cannot update its settings with invalid values.

        The serializer used by the view should already be tested by its own
        test case. As a result, it's not necessary to check an HTTP 400 Bad
        Request is returned for each invalid field. Checking ony the fields
        `comparison__criteria_order` and `criteria__display_order` should give
        us enough trust in the fact that the correct and already tested
        serializer is used by the view.
        """
        self.client.force_authenticate(self.user)

        self.user.settings = {
            "videos": {
                "rate_later__auto_remove": 4,
                "comparison__criteria_order": ["reliability"],
            }
        }
        self.user.save(update_fields=["settings"])

        # Invalid rate_later__auto_remove
        invalid_settings = {"videos": {"rate_later__auto_remove": 0}}
        response = self.client.patch(self.settings_base_url, data=invalid_settings, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("videos", response.data)
        self.assertIn("rate_later__auto_remove", response.data["videos"])

        # Invalid comparison__criteria_order
        invalid_settings_2 = {"videos": {"comparison__criteria_order": ["not_a_criteria"]}}
        response = self.client.patch(
            self.settings_base_url, data=invalid_settings_2, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("videos", response.data)
        self.assertIn("comparison__criteria_order", response.data["videos"])

        self.user.refresh_from_db()
        self.assertDictEqual(
            self.user.settings,
            {
                "videos": {
                    "rate_later__auto_remove": 4,
                    "comparison__criteria_order": ["reliability"],
                }
            },
        )

    def test_patch_without_initial_settings(self):
        """An authenticated user can update a subset of its settings."""
        self.client.force_authenticate(self.user)

        initial_settings = {}
        self.user.settings = initial_settings
        self.user.save(update_fields=["settings"])

        new_settings = {"videos": {"rate_later__auto_remove": 99}}
        response = self.client.patch(self.settings_base_url, data=new_settings, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual(
            response.data,
            new_settings,
            {"videos": {"rate_later__auto_remove": 99}},
        )
        self.user.refresh_from_db()
        self.assertDictEqual(self.user.settings, new_settings)
