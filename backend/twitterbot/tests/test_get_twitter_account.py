from twitterbot.uploader_twitter_account import get_twitter_account

# Those tests should probably be replaced by mock functions


def test_get_twitter_account():
    """Test get_twitter_account function"""

    assert get_twitter_account("dblEwDMeJTo") == "@le_science4all"

    assert get_twitter_account("VKsekCHBuHI") == "@HygieneMentale"

    assert get_twitter_account("u-rk8nRs4LA") is None
