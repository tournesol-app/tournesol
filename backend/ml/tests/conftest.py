from pytest import fixture


@fixture
def test_data():
    test_data = [
        (1, 100, 101, "test", 10, 0),
        (1, 101, 102, "test", 10, 0),
        (1, 104, 105, "test", 10, 0),
        (0, 100, 101, "test", -10, 0),
        (1, 104, 105, "test", 37 / 5 - 10, 0),
        (2, 104, 105, "test", 10, 0),
        (7, 966, 965, "test", 4 / 5 - 10, 0),
        (0, 100, 101, "largely_recommended", 10, 0),
    ]
    return test_data


@fixture
def training_data():
    training_data = [
        (1, 101, 102, "test", 10, 0),
        (2, 100, 101, "largely_recommended", 10, 0),
        (1, 104, 105, "test", 30 / 5 - 10, 0),
        (99, 100, 101, "largely_recommended", 10, 0),
        (2, 108, 107, "test", 10 / 5 - 10, 0),
        (0, 100, 102, "test", 70 / 5 - 10, 0),
        (0, 104, 105, "test", 70 / 5 - 10, 0),
        (0, 109, 110, "test", 0, 0),
        (2, 107, 108, "test", 10 / 5 - 10, 0),
        (1, 100, 101, "test", 10, 0),
        (3, 200, 201, "test", 85 / 5 - 10, 0),
    ]
    return training_data
