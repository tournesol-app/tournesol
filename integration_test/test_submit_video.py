import shortuuid
from helpers import do_api_call_v2, login, logout, TIME_WAIT
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_submit_video(driver):
    login(driver)

    print("Going to the expert interface...")
    expert_interface_btn = driver.find_element_by_id('expert_interface')
    expert_interface_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'video-left')))
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'video-right')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    # print("Skipping tutorial")
    # skip_tutorial_btn = driver.find_element_by_id('start_comparing_button')
    # skip_tutorial_btn.click()

    vid1 = shortuuid.ShortUUID().random(length=10)
    vid2 = shortuuid.ShortUUID().random(length=10)

    def set_video(which, vid_id):
        selector = driver.find_element_by_id(which)
        c = selector.find_element_by_class_name('video_id_text_field')
        c = c.find_elements_by_tag_name('input')[0]
        c.clear()
        c.send_keys(vid_id)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))
    set_video('video-left', vid1)
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))
    set_video('video-right', vid2)
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_submitted_text_info')))

    assert do_api_call_v2(driver, url=f"/videos/?video_id={vid1}")['count'] >= 1
    assert do_api_call_v2(driver, url=f"/videos/?video_id={vid2}")['count'] >= 1

    logout(driver)
