from helpers import login, logout, web_url


def test_premissions(driver):
    login(driver)

    driver.get(web_url + '/admin/')
    assert 'login' in driver.current_url

    driver.get(web_url + '/files/')
    assert '403 Forbidden' in driver.page_source

    driver.get(web_url)

    logout(driver)
