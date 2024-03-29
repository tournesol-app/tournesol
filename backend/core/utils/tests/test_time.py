from core.utils.time import time_ago, time_ahead


def test_time_ago():
    """Test method time_ago."""
    
    assert time_ago(hours=1) > time_ago(hours=10)
    assert time_ago(hours=10) > time_ago(days=1)
    assert time_ago(days=1) > time_ago(days=1, hours= 3)
    assert time_ago(days=6, hours=23) > time_ago(weeks=1)


def test_time_ahead():
    """Test method time_ahead."""
    
    assert time_ahead(hours=1) < time_ahead(hours=10)
    assert time_ahead(hours=10) < time_ahead(days=1)
    assert time_ahead(days=1) < time_ahead(days=1, hours= 3)
    assert time_ahead(days=6, hours=23) < time_ahead(weeks=1)
