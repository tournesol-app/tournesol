from solidago.generative_model import GenerativeModel

def test_generative_model():
    data = GenerativeModel()(50, 200)
    assert len(data.users) == 50
