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
    def setUp(self):
        self.entity_source = EntitySourceFactory(uid=CHANNEL_UID)

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
            {'name': None, 'thumbnail': None, 'customUrl': None}
        )

        # [WHEN] the metadata is a partial dict
        self.entity_source.metadata = {'name': 'channel_name'}
        # [THEN] `cleaned_metadata` returns valid metadata representation
        self.assertDictEqual(
            self.entity_source.cleaned_metadata,
            {'name': 'channel_name', 'thumbnail': None, 'customUrl': None}
        )

    def test_cleaned_metadata_with_invalid_medatadata(self):
        """
        Calling `cleaned_metadata` with invalid metadata values should
        raise an exception.
        """
        self.entity_source.metadata = {'name': [1, 2, 3]}
        with self.assertRaises(ValidationError):
            self.entity_source.cleaned_metadata

    def test_metadata_needs_to_be_refreshed(self):
        self.entity_source.last_metadata_request_at = None
        self.assertTrue(self.entity_source.metadata_needs_to_be_refreshed())

        self.entity_source.last_metadata_request_at = timezone.now() - timedelta(days=31)
        self.assertTrue(self.entity_source.metadata_needs_to_be_refreshed())

        self.entity_source.last_metadata_request_at = timezone.now() - timedelta(days=29)
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
        self.assertDictEqual(
            self.entity_source.metadata,
            {}
        )

        self.entity_source.update_metadata_field()
        self.assertDictEqual(
            self.entity_source.metadata,
            CHANNEL_METADATA
        )

        self.entity_source.refresh_from_db()
        self.assertDictEqual(
            self.entity_source.metadata,
            {}
        )
