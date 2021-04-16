import datetime


def from_list_by_key(lst, key, val):
    """Get an item from a list of dicts where key==val."""
    for item in lst:
        if item[key] == val:
            return item
    raise KeyError(f"{key}={val} not found in {lst}")


def get_singleton(lst):
    """Get the only item from the list."""
    assert len(lst) == 1, f"List was not a singleton {lst}"
    return lst[0]


def get_date_ago(**kwargs):
    """Get date in the past."""
    return (datetime.datetime.today() - datetime.timedelta(**kwargs)).date()
