from backend.models import ExpertRating, Video, UserPreferences, VideoRating,\
    ExpertRatingSliderChanges
from backend.rating_fields import VIDEO_FIELDS
from helpers import test_username, login, logout, set_slider_value, create_test_video, TIME_WAIT,\
    open_more_menu
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_representative(driver, django_db_blocker):
    # creating 2 videos
    video_ids = []
    with django_db_blocker.unblock():
        for _ in range(2):
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

        VideoRating.objects.create(video=videos[0], user=me, **{feature: 0}, **other_values)
        VideoRating.objects.create(video=videos[1], user=me, **{feature: 100}, **other_values)

    open_more_menu(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'representative_menu')))

    driver.find_element_by_id('representative_menu').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'representative_debug_slider')))

    sliders = driver.find_elements_by_class_name('representative_debug_slider')
    assert len(sliders) == 1

    set_slider_value(driver, slider=sliders[0], value=100)

    driver.find_element_by_class_name('representative_debug_submit').click()

    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_representative_interface_all')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_representative_not_loading'))
    )

    sliders = driver.find_elements_by_class_name('representative_debug_slider')
    assert len(sliders) == 0

    with django_db_blocker.unblock():
        assert ExpertRatingSliderChanges.objects.filter(context='DIS').count() > 0

    logout(driver)
