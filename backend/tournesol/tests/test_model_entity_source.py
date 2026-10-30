from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from tournesol.tests.factories.subscription import EntitySourceFactory

CHANNEL_ID = "UCH8TsmKEX_PR4jxsg2W3vOg"
CHANNEL_UID = f"yt:{CHANNEL_ID}"

CHANNEL_METADATA = {
    "name": "Tournesol",
    "thumbnail": "https://yt3.ggpht.com/medium",
    "customUrl": "Channel handle",
}


class EntitySourceTestCase(TestCase):

    OBSOLETE_METADATA_AFTER_DAYS = 7

    def setUp(self):
        self.entity_source = EntitySourceFactory(uid=CHANNEL_UID)

        self.metadata_timedelta_refresh_required = (
            EntitySourceTestCase.OBSOLETE_METADATA_AFTER_DAYS + 1
        )
        self.metadata_timedelta_refresh_notrequired = (
            EntitySourceTestCase.OBSOLETE_METADATA_AFTER_DAYS - 1
        )

    def test_cleaned_metadata_with_valid_medatadata(self):
        """
        Calling `cleaned_metadata` with valid metadata values should
        return the serialized metadata.
        """
        # [WHEN] the metadata is an empty dict
        self.entity_source.metadata = {}
        # [THEN] `cleaned_metadata` returns valid metadata representation
        self.assertDictEqual(
            self.entity_source.cleaned_metadata,
            {"name": None, "thumbnail": None, "customUrl": None},
        )

        # [WHEN] the metadata is a partial dict
        self.entity_source.metadata = {"name": "channel_name"}
        # [THEN] `cleaned_metadata` returns valid metadata representation
        self.assertDictEqual(
            self.entity_source.cleaned_metadata,
            {"name": "channel_name", "thumbnail": None, "customUrl": None},
        )

    def test_cleaned_metadata_with_invalid_medatadata(self):
        """
        Calling `cleaned_metadata` with invalid metadata values should
        raise an exception.
        """
        invalid_name_value = [1, 2, 3]
        self.entity_source.metadata = {"name": invalid_name_value}
        with self.assertRaises(ValidationError):
            self.entity_source.cleaned_metadata

    def test_metadata_needs_to_be_refreshed(self):
        self.entity_source.last_metadata_request_at = None
        self.assertTrue(self.entity_source.metadata_needs_to_be_refreshed())

        self.entity_source.last_metadata_request_at = timezone.now() - timedelta(
            days=self.metadata_timedelta_refresh_required
        )
        self.assertTrue(self.entity_source.metadata_needs_to_be_refreshed())

        self.entity_source.last_metadata_request_at = timezone.now() - timedelta(
            days=self.metadata_timedelta_refresh_notrequired
        )
        self.assertFalse(self.entity_source.metadata_needs_to_be_refreshed())

    @patch("tournesol.utils.api_youtube.get_channel_metadata")
    def test_update_metadata_field(self, mock_get_channel_metadata):
        """
        The method `update_metadata_field` should update the `EntitySource`
        instance's metadata field without saving it to the database.
        """
        mock_get_channel_metadata.return_value = CHANNEL_METADATA

        self.entity_source.metadata = {}
        self.entity_source.save(update_fields=["metadata"])

        self.entity_source.refresh_from_db()
        self.assertDictEqual(self.entity_source.metadata, {})

        self.entity_source.update_metadata_field()
        self.assertDictEqual(self.entity_source.metadata, CHANNEL_METADATA)

        self.entity_source.refresh_from_db()
        self.assertDictEqual(self.entity_source.metadata, {})

    @patch("tournesol.utils.api_youtube.get_channel_metadata")
    def test_refresh_metadata_with_default_args(self, mock_get_channel_metadata):
        """
        By default, calling `refresh_metadata` should update the `EntitySource`
        instance and save it to the database.
        """
        mock_get_channel_metadata.return_value = CHANNEL_METADATA

        # [WHEN] the matadata needs to be refreshed
        self.entity_source.metadata = {}
        self.entity_source.metadata_timestamp = None
        self.entity_source.last_metadata_request_at = None
        self.entity_source.save(
            update_fields=["metadata", "metadata_timestamp", "last_metadata_request_at"]
        )

        # By default, force=False and save=True
        self.entity_source.refresh_metadata()
        self.assertDictEqual(self.entity_source.metadata, CHANNEL_METADATA)
        self.assertIsNotNone(self.entity_source.metadata_timestamp)
        self.assertIsNotNone(self.entity_source.last_metadata_request_at)

        self.entity_source.refresh_from_db()
        self.assertDictEqual(self.entity_source.metadata, CHANNEL_METADATA)
        self.assertIsNotNone(self.entity_source.metadata_timestamp)
        self.assertIsNotNone(self.entity_source.last_metadata_request_at)

        # [WHEN] the matadata doesn't need to be refreshed
        metadata_updated_at = timezone.now() - timedelta(
            days=self.metadata_timedelta_refresh_notrequired
        )
        self.entity_source.metadata = {}
        self.entity_source.metadata_timestamp = metadata_updated_at
        self.entity_source.last_metadata_request_at = metadata_updated_at
        self.entity_source.save(
            update_fields=["metadata", "metadata_timestamp", "last_metadata_request_at"]
        )

        self.entity_source.refresh_metadata()
        self.assertDictEqual(self.entity_source.metadata, {})
        self.assertEqual(self.entity_source.metadata_timestamp, metadata_updated_at)
        self.assertEqual(self.entity_source.last_metadata_request_at, metadata_updated_at)

        self.entity_source.refresh_from_db()
        self.assertDictEqual(self.entity_source.metadata, {})
        self.assertEqual(self.entity_source.metadata_timestamp, metadata_updated_at)
        self.assertEqual(self.entity_source.last_metadata_request_at, metadata_updated_at)

    @patch("tournesol.utils.api_youtube.get_channel_metadata")
    def test_refresh_metadata_with_arg_force_set_to_true(self, mock_get_channel_metadata):
        """
        Using force=true should update the metadata regardless of the return
        value of `metadata_needs_to_be_refreshed`.
        """
        mock_get_channel_metadata.return_value = CHANNEL_METADATA

        metadata_updated_at = timezone.now() - timedelta(
            days=self.metadata_timedelta_refresh_notrequired
        )
        self.entity_source.metadata = {}
        self.entity_source.metadata_timestamp = metadata_updated_at
        self.entity_source.last_metadata_request_at = metadata_updated_at
        self.entity_source.save(
            update_fields=["metadata", "metadata_timestamp", "last_metadata_request_at"]
        )

        self.assertFalse(self.entity_source.metadata_needs_to_be_refreshed())

        self.entity_source.refresh_metadata(force=True)
        self.assertDictEqual(self.entity_source.metadata, CHANNEL_METADATA)
        self.assertIsNotNone(self.entity_source.metadata_timestamp)
        self.assertIsNotNone(self.entity_source.last_metadata_request_at)

        self.entity_source.refresh_from_db()
        self.assertDictEqual(self.entity_source.metadata, CHANNEL_METADATA)
        self.assertIsNotNone(self.entity_source.metadata_timestamp)
        self.assertIsNotNone(self.entity_source.last_metadata_request_at)

    @patch("tournesol.utils.api_youtube.get_channel_metadata")
    def test_refresh_metadata_with_arg_save_set_to_false(self, mock_get_channel_metadata):
        """
        Using save=false should update the `EntitySource` instansce's metadata
        field but not save it to the database.
        """
        mock_get_channel_metadata.return_value = CHANNEL_METADATA

        self.entity_source.metadata = {}
        self.entity_source.metadata_timestamp = None
        self.entity_source.last_metadata_request_at = None
        self.entity_source.save(
            update_fields=["metadata", "metadata_timestamp", "last_metadata_request_at"]
        )

        self.entity_source.refresh_metadata(save=False)
        self.assertDictEqual(self.entity_source.metadata, CHANNEL_METADATA)
        self.assertIsNotNone(self.entity_source.metadata_timestamp)
        self.assertIsNotNone(self.entity_source.last_metadata_request_at)

        self.entity_source.refresh_from_db()
        self.assertDictEqual(self.entity_source.metadata, {})
        self.assertIsNone(self.entity_source.metadata_timestamp)
        self.assertIsNone(self.entity_source.last_metadata_request_at)
