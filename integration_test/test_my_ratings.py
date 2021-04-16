from backend.models import ExpertRating, Video, UserPreferences
from backend.rating_fields import VIDEO_FIELDS
from helpers import test_username, login, logout, create_test_video, TIME_WAIT, open_more_menu
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_my_ratings(driver, django_db_blocker):
    # creating a video

    login(driver)

    with django_db_blocker.unblock():
        me = UserPreferences.objects.get(user__username=test_username)
        video_id1 = create_test_video()
        video_id2 = create_test_video()
        video_1 = Video.objects.get(video_id=video_id1)
        video_2 = Video.objects.get(video_id=video_id2)
        ExpertRating.objects.create(video_1=video_1, video_2=video_2,
                                    **{k: 50 for k in VIDEO_FIELDS},
                                    user=me)

    open_more_menu(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.visibility_of_element_located((By.ID, 'video_details_menu')))

    print("Going to the details page")
    expert_interface_btn = driver.find_element_by_id('video_details_menu')
    expert_interface_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'video_id_text_field')))

    elem = driver.find_element_by_class_name('video_id_text_field')
    elem = elem.find_element_by_tag_name('input')

    elem.clear()
    elem.send_keys(video_id1, Keys.HOME)
    if elem.get_attribute('value') != video_id1:
        elem.send_keys(3 * [Keys.DELETE])

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'button_video_ratings')))

    # opening ratings page
    driver.find_element_by_class_name('button_video_ratings').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_my_ratings')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'video_rating_video')))

    # have only 1 rating
    assert len(driver.find_elements_by_class_name('video_rating_video')) == 1

    # rerate
    driver.find_elements_by_class_name('video_rating_rerate')[0].click()

    # on the right page
    assert driver.current_url.split('/')[-2:] == [video_id1, video_id2]

    logout(driver)
