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
        self.valid_settings = {"videos": {"rate_later__auto_remove": 16}}

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
        new_settings = {"videos": {"rate_later__auto_remove": 99}}
        self.user.settings = new_settings
        self.user.save(update_fields=["settings"])
        response = self.client.get(self.settings_base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, new_settings)

    def test_anon_401_put(self):
        """An anonymous user cannot replace all its settings."""
        response = self.client.put(
            self.settings_base_url, data=self.valid_settings, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_200_put(self):
        """An authenticated user can replace all its settings."""
        self.client.force_authenticate(self.user)

        # [GIVEN] An initial set of settings, containing two scopes with extra
        # keys.
        initial_settings = {
            "videos": {"rate_later__auto_remove": 4, "extra_key": 99},
            "presidentielle2022": {"rate_later__auto_remove": 4, "extra_key": 99},
        }
        self.user.settings = initial_settings
        self.user.save(update_fields=["settings"])

        # [WHEN] The user replace its settings by new ones containing only one
        # scope and no extre key.
        new_settings = {"videos": {"rate_later__auto_remove": 99}}
        response = self.client.put(
            self.settings_base_url, data=new_settings, format="json"
        )
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
        response = self.client.patch(
            self.settings_base_url, data=new_settings, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        merged_settings = initial_settings.copy()
        merged_settings["videos"].update(new_settings["videos"])

        # [THEN] Only the provided keys of the provided scope should be
        # updated.

        # The API return the settings according ot its serializer...
        self.assertDictEqual(response.data, {"videos": {"rate_later__auto_remove": 99}})
        # ... but the database contains all saved settings.
        self.user.refresh_from_db()
        self.assertDictEqual(self.user.settings, merged_settings)

    def test_auth_400_patch_invalid_setting(self):
        """
        An authenticated user cannot update its settings with invalid values.
        """
        self.client.force_authenticate(self.user)

        self.user.settings = {"videos": {"rate_later__auto_remove": 4}}
        self.user.save(update_fields=["settings"])

        invalid_settings = {"videos": {"rate_later__auto_remove": 1}}
        response = self.client.patch(
            self.settings_base_url, data=invalid_settings, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("videos", response.data)
        self.assertIn("rate_later__auto_remove", response.data["videos"])
        self.user.refresh_from_db()
        self.assertDictEqual(
            self.user.settings, {"videos": {"rate_later__auto_remove": 4}}
        )
