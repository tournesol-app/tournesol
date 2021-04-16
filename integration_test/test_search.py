import numpy as np
from backend.rating_fields import VIDEO_FIELDS
from helpers import TIME_WAIT, login, logout, set_slider_value, do_api_call_v2,\
    create_test_video
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_user_ui_pref_videos(driver, django_db_blocker):
    """Test that user preferences are saved and videos are shown."""
    login(driver)

    with django_db_blocker.unblock():
        create_test_video(name="test")

    print("Going to user interface")
    ui_button = driver.find_element_by_id('user_interface')
    ui_button.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'search_phrase')))

    print("Typing search phrase")
    search_phrase_field = driver.find_element_by_id('search_phrase')
    search_phrase_field.clear()
    search_phrase_field.send_keys('test')

    # random preferences
    np.random.seed(42)
    values = np.random.rand(len(VIDEO_FIELDS)) * 100

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_search_not_loading')))

    for f, v in zip(VIDEO_FIELDS, values):
        set_slider_value(driver, s_id='preference_slider_' + f, value=v)

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_search_not_loading')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_search_not_loading')))

    print("Loading recommendations")
    load_rec_btn = driver.find_element_by_id("load_recommendations")
    load_rec_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_search_not_loading')))

    entry = do_api_call_v2(driver, url='/user_preferences/my/')
    values_got = [entry[x] for x in VIDEO_FIELDS]
    values_transformed = values / 2 + 50
    diff = np.max(np.abs(values_transformed - values_got))
    assert diff < 5, (values_transformed, values_got)
    print("Preferences normal", diff)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'video_search_result')))

    videos = driver.find_elements_by_class_name('video_search_result')
    assert videos, "No videos returned in search, or it took too long."
    print("Got", len(videos), "videos")
    logout(driver)
