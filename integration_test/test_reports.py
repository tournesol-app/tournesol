import numpy as np
from backend.models import VideoReports
from backend.rating_fields import VIDEO_REPORT_FIELDS
from helpers import login, logout, create_test_video, TIME_WAIT, open_more_menu
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_create_view_reports(driver, django_db_blocker):
    # creating a video

    with django_db_blocker.unblock():
        video_id = create_test_video()

    login(driver)

    open_more_menu(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.visibility_of_element_located((By.ID, 'video_details_menu')))

    print("Going to the details page")
    expert_interface_btn = driver.find_element_by_id('video_details_menu')
    expert_interface_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'video_id_text_field')))

    elem = driver.find_element_by_class_name('video_id_text_field')
    elem = elem.find_elements_by_tag_name('input')[0]
    elem.clear()
    elem.send_keys(video_id, Keys.HOME)
    if elem.get_attribute('value') != video_id:
        elem.send_keys(3 * [Keys.DELETE])
    print("target id", video_id)
    assert elem.get_attribute('value') == video_id

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'button_video_reports')))

    # going to reports page
    driver.find_element_by_class_name('button_video_reports').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'report_explanation')))

    assert not driver.find_elements_by_class_name('video_report_one_item')

    checked = {k: np.random.choice([True, False]) for k in VIDEO_REPORT_FIELDS}

    for k in VIDEO_REPORT_FIELDS:
        checkbox = driver.find_element_by_class_name(f'report_{k}_checkbox')
        if checked[k]:
            checkbox.click()
        assert checkbox.find_element_by_tag_name('input').get_property('checked') == checked[k]

    driver.find_element_by_class_name('report_explanation').find_element_by_tag_name(
        'textarea').send_keys(
        "Test explanation")

    driver.find_element_by_class_name('report_submit').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_report_submission_ok')))

    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'video_report_one_item')))

    assert len(driver.find_elements_by_class_name('video_report_one_item')) == 1

    with django_db_blocker.unblock():
        report = VideoReports.objects.get(video__video_id=video_id)
    assert report.explanation == "Test explanation"
    for k in VIDEO_REPORT_FIELDS:
        assert checked[k] == getattr(report, k)

    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'report_explanation')))

    # REPORT EDITING
    checked_old = checked
    checked = {k: np.random.choice([True, False]) for k in VIDEO_REPORT_FIELDS}

    for k in VIDEO_REPORT_FIELDS:
        checkbox = driver.find_element_by_class_name(f'report_{k}_checkbox')
        if checked_old[k] != checked[k]:
            checkbox.click()
        assert checkbox.find_element_by_tag_name('input').get_property('checked') == checked[k]

    elem = driver.find_element_by_class_name('report_explanation').find_element_by_tag_name(
        'textarea')
    elem.send_keys(
        " II")

    driver.find_element_by_class_name('report_submit').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_report_submission_ok')))

    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'report_explanation')))

    assert len(driver.find_elements_by_class_name('video_report_one_item')) == 1

    with django_db_blocker.unblock():
        report = VideoReports.objects.get(video__video_id=video_id)
    assert report.explanation == "Test explanation II"
    for k in VIDEO_REPORT_FIELDS:
        assert checked[k] == getattr(report, k)

    logout(driver)
