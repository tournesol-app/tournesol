from io import StringIO
from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.test import TestCase

from tournesol.models import Entity, EntitySource, EntitySourceLink
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.subscription import EntitySourceFactory, generate_youtube_channel_id

CHANNEL_ID = "UCH8TsmKEX_PR4jxsg2W3vOg"
CHANNEL_UID = f"yt:{CHANNEL_ID}"
OTHER_CHANNEL_ID = "UC1EacOJoqsKaYxaDomTCTEQ"
OTHER_CHANNEL_UID = f"yt:{OTHER_CHANNEL_ID}"


def create_video_without_source(channel_id):
    """Create a video as it was before entities were linked to their sources."""
    with patch.object(Entity, "update_sources"):
        return VideoFactory(metadata__channel_id=channel_id)


def fake_youtube_channels_response(channel_ids, missing_channel_ids=()):
    return {
        "items": [
            {"id": channel_id, "snippet": {"title": f"Channel {channel_id}"}}
            for channel_id in channel_ids
            if channel_id not in missing_channel_ids
        ]
    }


def run_link_entity_sources(*args):
    output = StringIO()
    call_command("link_entity_sources", *args, stdout=output)
    return output.getvalue()


@patch("tournesol.utils.api_youtube.get_youtube_channels_details")
class LinkEntitySourcesCommandTestCase(TestCase):
    def setUp(self):
        sleep_patcher = patch("tournesol.management.commands.link_entity_sources.time.sleep")
        self.mock_sleep = sleep_patcher.start()
        self.addCleanup(sleep_patcher.stop)

    def test_links_the_entities_without_source(self, mock_get_youtube_channels_details):
        mock_get_youtube_channels_details.side_effect = fake_youtube_channels_response
        videos = [
            create_video_without_source(CHANNEL_ID),
            create_video_without_source(CHANNEL_ID),
            create_video_without_source(OTHER_CHANNEL_ID),
        ]

        output = run_link_entity_sources()

        self.assertIn("2 unknown sources to fetch in 1 API calls", output)
        self.assertIn("API call 1/1: created 2 sources and 3 links.", output)
        self.assertIn("Done. 0 sources were not found on their platform.", output)
        self.assertEqual(videos[0].sources.get().uid, CHANNEL_UID)
        self.assertEqual(videos[1].sources.get().uid, CHANNEL_UID)
        self.assertEqual(videos[2].sources.get().uid, OTHER_CHANNEL_UID)
        source = EntitySource.objects.get(uid=CHANNEL_UID)
        self.assertEqual(source.metadata["name"], f"Channel {CHANNEL_ID}")
        self.assertIsNotNone(source.metadata_timestamp)

    def test_fetches_up_to_50_channels_per_api_call(self, mock_get_youtube_channels_details):
        mock_get_youtube_channels_details.side_effect = fake_youtube_channels_response
        for _ in range(60):
            create_video_without_source(generate_youtube_channel_id())

        output = run_link_entity_sources()

        self.assertIn("API call 1/2: created 50 sources and 50 links.", output)
        self.assertIn("API call 2/2: created 10 sources and 10 links.", output)
        requested_counts = [
            len(call.args[0]) for call in mock_get_youtube_channels_details.call_args_list
        ]
        self.assertEqual(requested_counts, [50, 10])

    def test_paces_the_api_calls_to_the_daily_budget(self, mock_get_youtube_channels_details):
        mock_get_youtube_channels_details.side_effect = fake_youtube_channels_response
        for _ in range(120):
            create_video_without_source(generate_youtube_channel_id())

        output = run_link_entity_sources("--api-calls-per-day", "100")

        self.assertIn("in 3 API calls, one every 864 seconds.", output)
        self.assertEqual(
            [call.args[0] for call in self.mock_sleep.call_args_list], [864.0, 864.0]
        )

    def test_default_pace_is_1000_api_calls_per_day(self, mock_get_youtube_channels_details):
        mock_get_youtube_channels_details.side_effect = fake_youtube_channels_response
        create_video_without_source(CHANNEL_ID)

        output = run_link_entity_sources()

        self.assertIn("one every 86 seconds.", output)

    def test_rejects_a_non_positive_pace(self, _mock_get_youtube_channels_details):
        with self.assertRaisesMessage(CommandError, "--api-calls-per-day must be positive"):
            run_link_entity_sources("--api-calls-per-day", "0")

    def test_known_sources_are_linked_without_api_call(self, mock_get_youtube_channels_details):
        source = EntitySourceFactory(uid=CHANNEL_UID)
        video = create_video_without_source(CHANNEL_ID)

        output = run_link_entity_sources()

        self.assertIn("Created 1 links to 1 known sources. 0 unknown sources", output)
        self.assertEqual(list(video.sources.all()), [source])
        mock_get_youtube_channels_details.assert_not_called()

    def test_channel_missing_on_youtube_is_not_linked(self, mock_get_youtube_channels_details):
        mock_get_youtube_channels_details.side_effect = (
            lambda channel_ids: fake_youtube_channels_response(
                channel_ids, missing_channel_ids=[OTHER_CHANNEL_ID]
            )
        )
        video = create_video_without_source(CHANNEL_ID)
        video_of_missing_channel = create_video_without_source(OTHER_CHANNEL_ID)

        output = run_link_entity_sources()

        self.assertIn("API call 1/1: created 1 sources and 1 links.", output)
        self.assertIn("Done. 1 sources were not found on their platform.", output)
        self.assertEqual(video.sources.get().uid, CHANNEL_UID)
        self.assertFalse(video_of_missing_channel.sources.exists())

    def test_api_error_stops_and_a_new_run_continues(self, mock_get_youtube_channels_details):
        def second_call_fails(channel_ids):
            if mock_get_youtube_channels_details.call_count == 2:
                raise Exception("quotaExceeded")  # pylint: disable=broad-exception-raised
            return fake_youtube_channels_response(channel_ids)

        mock_get_youtube_channels_details.side_effect = second_call_fails
        for _ in range(60):
            create_video_without_source(generate_youtube_channel_id())

        with self.assertRaisesMessage(CommandError, "API call 2 failed"):
            run_link_entity_sources()

        self.assertEqual(EntitySource.objects.count(), 50)
        self.assertEqual(EntitySourceLink.objects.count(), 50)

        output = run_link_entity_sources()

        self.assertIn("API call 1/1: created 10 sources and 10 links.", output)
        self.assertEqual(EntitySourceLink.objects.count(), 60)

    def test_running_twice_creates_nothing_more(self, mock_get_youtube_channels_details):
        mock_get_youtube_channels_details.side_effect = fake_youtube_channels_response
        create_video_without_source(CHANNEL_ID)
        run_link_entity_sources()

        output = run_link_entity_sources()

        self.assertIn("Created 0 links to 0 known sources. 0 unknown sources", output)
        self.assertEqual(mock_get_youtube_channels_details.call_count, 1)
