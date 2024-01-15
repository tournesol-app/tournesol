""" Helpers to manipulate time and dates """

from datetime import datetime
from datetime import timedelta

def week_date_to_week_number(week_date: str, week_date0: str = "2021-01-11") -> int:
    """ week dates are given as strings in Tournesol's dataset.
    This simple function turns them into week numbers.
    """
    date = datetime.fromisoformat(week_date)
    date0 = datetime.fromisoformat(week_date0)
    return int((date - date0).days / 7)

def week_number_to_week_date(week_number: int, week_date0: str = "2021-01-11") -> str:
    date = datetime.fromisoformat(week_date0) + timedelta(weeks=week_number)
    return date.isoformat()[:10]
