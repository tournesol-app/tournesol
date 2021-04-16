from backend.models import ExpertRating, Video, UserPreferences, ExpertRatingSliderChanges
from backend.rating_fields import VIDEO_FIELDS
from helpers import test_username, login, logout, set_slider_value, create_test_video,\
    open_more_menu, TIME_WAIT
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_cyclic_create_view_resolve(driver, django_db_blocker):
    # creating 3 videos
    video_ids = []
    with django_db_blocker.unblock():
        for _ in range(3):
            video_ids.append(create_test_video())
        videos = [Video.objects.get(video_id=vid) for vid in video_ids]

    login(driver)

    with django_db_blocker.unblock():
        me = UserPreferences.objects.get(user__username=test_username)

    # creating ratings
    feature = VIDEO_FIELDS[0]
    other_values = {k: 50 for k in VIDEO_FIELDS if k != feature}
    with django_db_blocker.unblock():
        ExpertRating.objects.create(video_1=videos[0], video_2=videos[1], **other_values,
                                    **{feature: 0}, user=me)  # left is better
        ExpertRating.objects.create(video_1=videos[1], video_2=videos[2], **other_values,
                                    **{feature: 0}, user=me)  # left is better
        ExpertRating.objects.create(video_1=videos[2], video_2=videos[0], **other_values,
                                    **{feature: 0}, user=me)  # left is better

    open_more_menu(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.visibility_of_element_located((By.ID, 'inconsistencies_menu')))

    driver.find_element_by_id('inconsistencies_menu').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'inconsistency')))

    incons = driver.find_elements_by_class_name('inconsistency')

    assert len(incons) > 0

    for inc in incons:
        vids = inc.get_attribute('id').split('_')
        assert len(vids) == 2
        assert all([v in video_ids for v in vids])

    incons[0].find_element_by_class_name('inconsistency_slider')

    set_slider_value(driver, slider=incons[0].find_element_by_class_name('inconsistency_slider'),
                     value=100)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'inconsistency_submit')))

    driver.find_element_by_class_name('inconsistency_submit').click()

    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_all_inconsistencies')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_inconsistencies_not_loading'))
    )

    incons = driver.find_elements_by_class_name('inconsistency')
    assert not incons

    with django_db_blocker.unblock():
        assert ExpertRatingSliderChanges.objects.filter(context='INC').count() > 0

    logout(driver)
