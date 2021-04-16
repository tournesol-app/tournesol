import datetime
from uuid import uuid1

import numpy as np
from backend.models import Video, DjangoUser, VideoRating, UserInformation, UserPreferences, \
    VideoRatingPrivacy
from backend.rating_fields import VIDEO_FIELDS
from helpers import login, logout, test_username, create_test_video, \
    random_alphanumeric, do_api_call_v2, TIME_WAIT
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_representative_privacy(driver, django_db_blocker):
    with django_db_blocker.unblock():
        u = DjangoUser.objects.create(username=random_alphanumeric(), is_active=True)
        UserInformation.objects.create(user=u, show_my_profile=False)

        u1 = DjangoUser.objects.create(username=random_alphanumeric(), is_active=True)
        UserInformation.objects.create(user=u1, show_my_profile=True)
        up1 = UserPreferences.objects.create(user=u1)

        v = Video.objects.create(video_id=random_alphanumeric(), name="test",
                                 **{f: 10 for f in VIDEO_FIELDS})
        VideoRating.objects.create(user=up1, video=v, **{f: 10 for f in VIDEO_FIELDS})

        u2 = DjangoUser.objects.create(username=random_alphanumeric(), is_active=True)
        UserInformation.objects.create(user=u2, show_my_profile=False)
        up2 = UserPreferences.objects.create(user=u2)
        VideoRating.objects.create(user=up2, video=v, **{f: 10 for f in VIDEO_FIELDS})
        VideoRatingPrivacy.objects.create(video=v, user=up2, is_public=True)

        u3 = DjangoUser.objects.create(username=random_alphanumeric(), is_active=True)
        UserInformation.objects.create(user=u3, show_my_profile=False)
        up3 = UserPreferences.objects.create(user=u3)
        VideoRating.objects.create(user=up3, video=v, **{f: 10 for f in VIDEO_FIELDS})
        VideoRatingPrivacy.objects.create(video=v, user=up3, is_public=False)

    login(driver)

    results = do_api_call_v2(driver, '/user_information/public_models/')
    results = [x['username'] for x in results['results']]
    assert test_username in results

    # no videos
    assert u.username not in results

    # default value
    if VideoRatingPrivacy.DEFAULT_VALUE_IS_PUBLIC:
        assert u1.username in results
    else:
        assert u1.username not in results

    # public (explicitly)
    assert u2.username in results

    # private (explicitly)
    assert u3.username not in results

    # no videos for myself, but allowed to search with own username anyway
    assert do_api_call_v2(driver, '/videos/search_tournesol/?search_model=' + test_username,
                          expect_fail=True).ok

    # u1 is either private or public (default value)
    if VideoRatingPrivacy.DEFAULT_VALUE_IS_PUBLIC:
        r1 = do_api_call_v2(driver,
                            '/videos/search_tournesol/?reliability=1&search_model=' + u1.username)
        assert len(r1['results']) == 1
    else:
        assert do_api_call_v2(
            driver, '/videos/search_tournesol/?reliability=1&search_model=' + u1.username,
            expect_fail=True).status_code == 403

    # u2 has public videos
    r1 = do_api_call_v2(driver,
                        '/videos/search_tournesol/?reliability=1&search_model=' + u2.username)
    assert len(r1['results']) == 1

    # u/u3 doesn't have public videos
    assert do_api_call_v2(driver, '/videos/search_tournesol/?search_model=' + u.username,
                          expect_fail=True).status_code == 403
    assert do_api_call_v2(driver, '/videos/search_tournesol/?search_model=' + u3.username,
                          expect_fail=True).status_code == 403

    if VideoRatingPrivacy.DEFAULT_VALUE_IS_PUBLIC:
        with django_db_blocker.unblock():
            VideoRatingPrivacy.objects.create(video=v, user=up1, is_public=False)

        assert do_api_call_v2(
            driver, '/videos/search_tournesol/?reliability=1&search_model=' + u1.username,
            expect_fail=True).status_code == 403

        results = do_api_call_v2(driver, '/user_information/public_models/')
        assert u1.username not in results
    else:
        with django_db_blocker.unblock():
            VideoRatingPrivacy.objects.create(video=v, user=up1, is_public=True)

        r1 = do_api_call_v2(driver,
                            '/videos/search_tournesol/?reliability=1&search_model=' + u1.username)
        assert len(r1['results']) == 1

        results = do_api_call_v2(driver, '/user_information/public_models/')
        assert u1.username in results

    logout(driver)

    with django_db_blocker.unblock():
        u.delete()


def select_options(driver, key, value):
    """Select an option in search options."""
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'all_search_options')))
    labels = driver.find_element_by_class_name('all_search_options').find_elements_by_tag_name(
        'label')
    label = [x for x in labels if x.text == key][0]
    idx = labels.index(label)
    select = driver.find_element_by_class_name(
        'all_search_options').find_elements_by_tag_name('select')[idx]
    select.click()
    options = select.find_elements_by_tag_name('option')
    option = [x for x in options if x.get_attribute('text') == value][0]
    option.click()


def test_representative_search(driver, django_db_blocker):
    with django_db_blocker.unblock():
        u = DjangoUser.objects.create(username=random_alphanumeric(), is_active=True)
        up = UserPreferences.objects.create(user=u)
        UserInformation.objects.create(user=u, show_my_profile=True)
        video_id = create_test_video()
        video = Video.objects.get(video_id=video_id)
        ratings = {f: np.random.randn() for f in VIDEO_FIELDS}
        VideoRating.objects.create(user=up, video=video, **ratings)
        VideoRatingPrivacy.objects.create(user=up, video=video, is_public=True)

    login(driver)

    ui_button = driver.find_element_by_id('user_interface')
    ui_button.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'search_options')))

    driver.find_element_by_class_name('search_options').click()
    inp_model = driver.find_element_by_id('autocomplete_search_model')
    inp_model.send_keys(len('Aggregated') * [Keys.BACK_SPACE])
    inp_model.send_keys(f"{u.username}'s representative")
    driver.find_element_by_class_name('MuiAutocomplete-popper').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_search_not_loading')))

    print("Loading recommendations")
    load_rec_btn = driver.find_element_by_id("load_recommendations")
    load_rec_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_search_not_loading')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, f'video_card_id_{video_id}')))

    # now will only see 1 video
    assert driver.find_elements_by_class_name(f'video_card_id_{video_id}')

    logout(driver)

    with django_db_blocker.unblock():
        u.delete()
        Video.objects.filter(video_id=video_id).delete()


def test_filters(driver, django_db_blocker):
    login(driver)

    ui_button = driver.find_element_by_id('user_interface')
    ui_button.click()

    unique_substr = str(uuid1())

    # creating videos
    with django_db_blocker.unblock():
        video_ids = [create_test_video() for _ in range(3)]
        videos = [Video.objects.get(video_id=vid) for vid in video_ids]
        for v in videos:
            v.name = unique_substr + " " + v.name
            for f in VIDEO_FIELDS:
                setattr(v, f, 1e10)
            v.save()

        videos[0].duration = datetime.timedelta(minutes=18)
        videos[0].views = 9999
        videos[0].publication_date = datetime.datetime.now() - datetime.timedelta(days=1)
        videos[0].language = 'en'
        videos[0].save()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'search_phrase')))

    # setting search field
    search_phrase_field = driver.find_element_by_id('search_phrase')
    search_phrase_field.clear()
    search_phrase_field.send_keys(unique_substr)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_search_not_loading')))

    # can get all videos
    print("Loading recommendations")
    load_rec_btn = driver.find_element_by_id("load_recommendations")
    load_rec_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_search_not_loading')))

    target_classname = f'video_card_id_{video_ids[-1]}'
    print(video_ids, video_ids[-1], target_classname)
    WebDriverWait(driver, TIME_WAIT * 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, target_classname)))

    videos_out = [x for video_id in video_ids for x in
                  driver.find_elements_by_class_name(f'video_card_id_{video_id}')]
    print(videos_out)
    assert len(videos_out) == len(videos)

    # target search options
    values = {
        'Minimum Duration': '15 min',
        'Maximum Duration': '30 min',
        'Minimum Number of Views': '0 views',
        'Maximum Number of Views': '10k views',
        'Publication Date': 'Last month',
        'Language': 'English'
    }

    # opening search options
    driver.find_element_by_class_name('search_options').click()

    # setting options
    for key, value in values.items():
        select_options(driver, key, value)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_search_not_loading')))

    print("Loading recommendations")
    load_rec_btn = driver.find_element_by_id("load_recommendations")
    load_rec_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_search_not_loading')))

    target_classname = f'video_card_id_{video_ids[0]}'
    print(video_ids, target_classname)
    WebDriverWait(driver, TIME_WAIT * 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, target_classname)))

    # now will only see 1 video
    videos_out = [x for video_id in video_ids for x in
                  driver.find_elements_by_class_name(f'video_card_id_{video_id}')]
    assert len(videos_out) == 1

    logout(driver)
