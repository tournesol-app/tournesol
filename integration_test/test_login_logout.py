from helpers import login, logout, open_more_menu, close_more_menu, TIME_WAIT, open_tournesol
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_login_logout(driver):
    """Test that we can log in and log out."""
    login(driver)
    logout(driver)


def test_menu_open_close_nologin(driver):
    open_tournesol(driver)

    open_more_menu(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_list_more')))

    close_more_menu(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_more_closed')))


def test_menu_open_close_login(driver):
    login(driver)

    open_more_menu(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_list_more')))

    close_more_menu(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_more_closed')))

    logout(driver)
