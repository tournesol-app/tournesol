from pathlib import Path
from unittest.mock import MagicMock, patch

from twitterbot.uploader_twitter_account import get_twitter_account_from_channel_id


@patch("twitterbot.uploader_twitter_account.requests.get")
def test_get_twitter_account_from_channel_id(mock_requests):
    """Test function for get_twitter_account_from_channel_id"""

    # Correct response from youtube
    mock_resp = Path("./twitterbot/tests/mock_resp.txt").read_text()
    mock_requests.return_value = MagicMock(status_code=200, text=mock_resp)

    assert (
        get_twitter_account_from_channel_id("UC0NCbj8CxzeCGIF6sODJ-7A")
        == "@le_science4all"
    )

    # Bad response ("This channel does not exist.")
    mock_bad_resp = Path("./twitterbot/tests/mock_bad_resp.txt").read_text()
    mock_requests.return_value = MagicMock(status_code=200, text=mock_bad_resp)

    assert get_twitter_account_from_channel_id("UC0NCbj8CxzeCGIF6sOZZZZZ") is None
