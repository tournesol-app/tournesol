from backend.constants import minNumRateLater, n_top_popular
from backend.models import Video, UserPreferences, VideoRateLater, DjangoUser
from django.db.models import Max, F
from helpers import test_username, login, logout, create_test_video, \
    TIME_WAIT, random_alphanumeric, web_url, element_present_now, get_object_with_timeout
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_home_page_link_smaller(driver, django_db_blocker):
    login(driver)
    with django_db_blocker.unblock():
        VideoRateLater.objects.filter(user__user__username=test_username).delete()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_home_toratelater')))

    driver.find_element_by_id('id_home_toratelater').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_ratelater_page_all')))

    logout(driver)


def test_home_page_link_enough(driver, django_db_blocker):
    with django_db_blocker.unblock():
        VideoRateLater.objects.filter(user__user__username=test_username).delete()
        video_ids = [create_test_video() for _ in range(minNumRateLater)]
        videos = [Video.objects.get(video_id=vid) for vid in video_ids]
        dj_u = DjangoUser.objects.get(username=test_username)
        up, _ = UserPreferences.objects.get_or_create(user=dj_u)
        [VideoRateLater.objects.create(video=v, user=up) for v in videos]

    login(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_home_toexpert')))

    driver.find_element_by_id('id_home_toexpert').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    logout(driver)


def test_rate_later_top_k(driver, django_db_blocker):
    # creating popular videos...
    with django_db_blocker.unblock():

        # determining current max views...
        max_views = 0
        if Video.objects.all().count() > 0:
            max_views = Video.objects.all().aggregate(Max(F('views')))['views__max']

        video_ids = [random_alphanumeric() for _ in range(n_top_popular)]
        Video.objects.bulk_create([Video(video_id=vid, views=max_views + 1)
                                   for vid in video_ids])
        VideoRateLater.objects.filter(user__user__username=test_username).delete()
        video_ids_set = set(video_ids)

    login(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'rate_later_menu')))

    print("Going to the rate later page")
    expert_interface_btn = driver.find_element_by_id('rate_later_menu')
    expert_interface_btn.click()

    assert not element_present_now(driver, 'id_controls_prev_next')
    assert not element_present_now(driver, 'id_big_expert_interface')

    def add_from_topk():
        # requesting new video
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'new_video_button')))

        elems = driver.find_elements_by_class_name('new_video_button')
        assert len(elems) == 1
        elems[0].click()

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_top_video_videocard')))

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_big_add_rate_later')))

        driver.find_element_by_id('id_big_add_rate_later').click()

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_rate_later_submit_ok')))

        with django_db_blocker.unblock():
            ids_vrl = list(VideoRateLater.objects.filter(
                user__user__username=test_username).values('video__video_id'))
            ids_vrl = [x['video__video_id'] for x in ids_vrl]
        assert set(ids_vrl).issubset(video_ids_set)
        return len(ids_vrl)

    for i in range(1, minNumRateLater + 2):
        assert add_from_topk() == i

        if i >= minNumRateLater:
            WebDriverWait(driver, TIME_WAIT).until(
                EC.presence_of_element_located((By.ID, 'id_big_expert_interface')))
        else:
            WebDriverWait(driver, TIME_WAIT).until(
                EC.presence_of_element_located((By.ID, 'id_recommend_add_more')))

    # trying to add manually now...

    elem = driver.find_element_by_class_name('video_id_text_field')
    elem = elem.find_element_by_tag_name('input')

    elem.clear()
    elem.send_keys('abacaba')

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_big_add_rate_later')))

    driver.find_element_by_id('id_big_add_rate_later').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_rate_later_submit_ok')))

    with django_db_blocker.unblock():
        get_object_with_timeout(VideoRateLater, user__user__username=test_username,
                                video__video_id='abacaba')

    logout(driver)


def test_submit_to_add_later_url(driver, django_db_blocker):
    """Add video to rate later list via a URL."""
    login(driver)

    video_id = random_alphanumeric()

    driver.get(web_url + '/rate_later_add/' + video_id)

    # checking that submission succeeded
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_rate_later_submit_ok')))

    # checking that list is present
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_rate_later_list')))

    # checking that the video is in the list
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, f'id_{video_id}_remove_rate_later')))

    # doing the same thing, but now will get a warning
    driver.refresh()

    # checking that submission succeeded
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_rate_later_submit_already_exists')))

    # checking that list is present
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_rate_later_list')))

    # checking that the video is in the list
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, f'id_{video_id}_remove_rate_later')))

    with django_db_blocker.unblock():
        Video.objects.filter(video_id=video_id).delete()

    logout(driver)


def test_add_delete(driver, django_db_blocker):
    """Add/delete videos to/from rate later."""
    login(driver)

    n_videos = 15
    limit = 5

    with django_db_blocker.unblock():
        up = UserPreferences.objects.get(user__username=test_username)
        video_ids = [create_test_video() for _ in range(n_videos)]
        videos = [Video.objects.get(video_id=vid) for vid in video_ids]
        vrls = [VideoRateLater.objects.create(user=up, video=v) for v in videos]
        vrls_reverse = vrls[::-1]

    print("Going to the rate later page")
    expert_interface_btn = driver.find_element_by_id('rate_later_menu')
    expert_interface_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_rate_later_list')))

    # should get 5 "remove from rate later" buttons
    offset = 0
    for v in vrls_reverse[offset:offset + limit]:
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, f'id_{v.video.video_id}_remove_rate_later')))

    # removing the first one
    driver.find_element_by_id(f'id_{vrls_reverse[0].video.video_id}_remove_rate_later').click()

    # waiting until the 'add' button appears
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID,
                                        f'id_{vrls_reverse[0].video.video_id}_rate_later')))

    # checking that there is no corresponding vrl
    with django_db_blocker.unblock():
        assert VideoRateLater.objects.filter(video=vrls_reverse[0].video,
                                             user=up).count() == 0

    # adding to Rate Later again
    driver.find_element_by_id(f'id_{vrls_reverse[0].video.video_id}_rate_later').click()

    # waiting until the 'remove' button appears
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID,
                                        f'id_{vrls_reverse[0].video.video_id}_remove_rate_later')))

    # checking that there is a corresponding entry
    with django_db_blocker.unblock():
        assert VideoRateLater.objects.filter(video=vrls_reverse[0].video,
                                             user=up).count() == 1

    # clicking on the 'next' button
    driver.find_element_by_id('id_rate_later_next').click()

    # waiting for videos...
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_rate_later_list')))

    # verifying the new list
    offset = 5
    for v in vrls_reverse[offset:offset + limit]:
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, f'id_{v.video.video_id}_remove_rate_later')))

    # going back
    driver.find_element_by_id('id_rate_later_prev').click()

    # waiting for videos...
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_rate_later_list')))

    # should get 5 "remove from rate later" buttons, like before
    offset = 0
    for v in vrls_reverse[offset:offset + limit]:
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, f'id_{v.video.video_id}_remove_rate_later')))

    logout(driver)

    with django_db_blocker.unblock():
        for v in videos:
            v.delete()
