from twitterbot.uploader_twitter_account import get_twitter_account_from_uploader_id
from unittest.mock import MagicMock, patch


@patch("twitterbot.uploader_twitter_account.requests.get")
def test_get_twitter_account_from_uploader_id(mock_requests):
    """Test function for get_twitter_account_from_uploader_id"""

    # Correct response from youtube
    with open("./twitterbot/tests/mock_resp.txt") as f:
        mock_resp = f.read()

    mock_requests.return_value = MagicMock(status_code=200, text=mock_resp)

    assert (
        get_twitter_account_from_uploader_id("UC0NCbj8CxzeCGIF6sODJ-7A")
        == "@le_science4all"
    )

    # Bad response ("This channel does not exist."
    with open("./twitterbot/tests/mock_bad_resp.txt") as f:
        mock_bad_resp = f.read()

    mock_requests.return_value = MagicMock(status_code=200, text=mock_bad_resp)

    assert get_twitter_account_from_uploader_id("UC0NCbj8CxzeCGIF6sOZZZZZ") is None
