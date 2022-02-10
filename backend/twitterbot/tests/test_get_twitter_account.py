from twitterbot.uploader_twitter_account import get_uploader_id, get_twitter_account

# Those tests should probably be replaced by mock functions


def test_get_uploader_id():
    """Test get_uploader_id function"""

    assert get_uploader_id("dblEwDMeJTo") == "UC0NCbj8CxzeCGIF6sODJ-7A"

    assert get_uploader_id("VKsekCHBuHI") == "UCMFcMhePnH4onVHt2-ItPZw"

    assert get_uploader_id("NotARealID") is None


def test_get_twitter_account():
    """Test get_twitter_account function"""

    assert get_twitter_account("dblEwDMeJTo") == "@le_science4all"

    assert get_twitter_account("VKsekCHBuHI") == "@HygieneMentale"

    assert get_twitter_account("u-rk8nRs4LA") is None
