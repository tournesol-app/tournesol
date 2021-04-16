from helpers import web_url, test_username, test_password, do_api_call_v2
from requests import post
from frontend.views import create_user_preferences


def get_token(username, password):
    response = post(web_url + "/api-token-auth/", {'username': username,
                                                   'password': password})
    assert response.ok
    return str(response.json()['token'])


def test_get_token():
    token = get_token(test_username, test_password)
    assert token


def test_api_call(driver, django_db_blocker):
    with django_db_blocker.unblock():
        create_user_preferences()
    token = get_token(test_username, test_password)
    result = do_api_call_v2(driver, '/user_preferences/my/',
                            headers={'Authorization': f"Token {token}"},
                            cookie_auth=False)
    assert 'id' in result
    print(result)
