from solidago.poll.tournesol_export import TournesolExport

def test_week_date_to_week_number():
    assert TournesolExport.week_date_to_week_number("2021-01-15") == 0
    assert TournesolExport.week_date_to_week_number("2021-01-26") == 2
    assert TournesolExport.week_date_to_week_number("2021-02-01") == 3

def test_week_number_to_week_date():
    assert TournesolExport.week_number_to_week_date(0) == "2021-01-11T00:00:00"
    assert TournesolExport.week_number_to_week_date(2) == "2021-01-25T00:00:00"
