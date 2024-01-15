from solidago.utils import date

def test_week_date_to_week_number():
    assert date.week_date_to_week_number("2021-01-15") == 0
    assert date.week_date_to_week_number("2021-01-26") == 2
    assert date.week_date_to_week_number("2021-02-01") == 3

def test_week_number_to_week_date():
    assert date.week_number_to_week_date(0) == "2021-01-11"
    assert date.week_number_to_week_date(2) == "2021-01-25"
