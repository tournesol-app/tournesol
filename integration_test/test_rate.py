import string

import editdistance
import numpy as np
import shortuuid
from annoying.functions import get_object_or_None
from backend.constants import featureIsEnabledByDeFault
from backend.models import ExpertRating, UserPreferences, Video, VideoSelectorSkips, \
    UserInformation, DjangoUser, VideoRatingPrivacy, VideoRateLater, ExpertRatingSliderChanges,\
    EmailDomain, VerifiableEmail
from backend.rating_fields import VIDEO_FIELDS
from helpers import web_url, test_username, login, logout, set_slider_value, do_api_call_v2, \
    random_alphanumeric, TIME_WAIT, filter_object_with_timeout, create_test_video, \
    get_object_with_timeout, get
from requests import post
from selenium import webdriver  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402
import clipboard
from selenium.webdriver.common.keys import Keys


def fill_rate_later(django_db_blocker):
    with django_db_blocker.unblock():
        dj_u = DjangoUser.objects.get(username=test_username)
        up, _ = UserPreferences.objects.get_or_create(user=dj_u)
        video_ids = [create_test_video() for _ in range(10)]
        videos = [Video.objects.get(video_id=vid) for vid in video_ids]
        [VideoRateLater.objects.create(user=up, video=v) for v in videos]


def cleanup_rate_later(django_db_blocker):
    with django_db_blocker.unblock():
        UserPreferences.objects.filter(user__username=test_username).delete()


def set_all_features_enabled(django_db_blocker):
    """Enable all quality features."""
    with django_db_blocker.unblock():
        updated = UserPreferences.objects.filter(user__username=test_username).update(**{
            f + "_enabled": True
            for f in VIDEO_FIELDS
        })
        return updated


def test_set_privacy_settings(driver, django_db_blocker):
    cleanup_rate_later(django_db_blocker)

    with django_db_blocker.unblock():
        video_id1 = create_test_video()
        video_id2 = create_test_video()
        u = DjangoUser.objects.get(username=test_username)
        ui, _ = UserInformation.objects.get_or_create(user=u)
        ui.show_my_profile = True
        ui.save()

        up, _ = UserPreferences.objects.get_or_create(user=u)
        EmailDomain.objects.create(domain="@tournesol.app", status=EmailDomain.STATUS_ACCEPTED)
        VerifiableEmail.objects.create(user=ui, email="test@tournesol.app",
                                       is_verified=True)
        ExpertRating.objects.create(user=up, video_1=Video.objects.get(video_id=video_id1),
                                    video_2=Video.objects.get(video_id=video_id2))

    login(driver)

    fill_rate_later(django_db_blocker)

    set_all_features_enabled(django_db_blocker)

    driver.get(web_url + '/rate/' + video_id1 + '/' + video_id2)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_expert_rating_page')))

    def check_privacy_status(video_id1, is_private, check_db=True,
                             check_api=False):
        priv_public = 'private' if is_private else 'public'
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, f'id_video_{video_id1}_{priv_public}'))
        )

        if check_db:
            with django_db_blocker.unblock():
                get_object_with_timeout(VideoRatingPrivacy,
                                        video__video_id=video_id1,
                                        user=up, is_public=not is_private)

        if check_api:
            pe = do_api_call_v2(driver, '/videos/?video_id=' + video_id1)['results'][0][
                'public_experts']
            if is_private:
                assert len(pe) == 0
            else:
                assert len(pe) == 1, pe
                assert pe[0]['username'] == test_username

    def set_privacy(video_id1, is_private):
        # opening the privacy menu...
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, f'id_open_privacy_menu_{video_id1}')))

        driver.find_element_by_id(f'id_open_privacy_menu_{video_id1}').click()

        priv_true_false = 'true' if is_private else 'false'

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID,
                                            f'menu_set_private_{priv_true_false}_{video_id1}'))
        )

        driver.find_element_by_id(f'menu_set_private_{priv_true_false}_{video_id1}').click()

        WebDriverWait(driver, TIME_WAIT).until(
            EC.element_to_be_clickable((By.ID, f'id_open_privacy_menu_{video_id1}'))
        )

    original_is_private = not VideoRatingPrivacy.DEFAULT_VALUE_IS_PUBLIC
    check_privacy_status(video_id1, original_is_private, check_db=False)

    set_privacy(video_id1, not original_is_private)
    check_privacy_status(video_id1, not original_is_private, check_api=True)

    set_privacy(video_id1, original_is_private)
    check_privacy_status(video_id1, original_is_private, check_api=True)

    logout(driver)

    cleanup_rate_later(django_db_blocker)


def test_already_rated_videos(driver, django_db_blocker):
    login(driver)

    cleanup_rate_later(django_db_blocker)
    fill_rate_later(django_db_blocker)

    set_all_features_enabled(django_db_blocker)

    print("Going to the expert interface...")
    expert_interface_btn = driver.find_element_by_id('expert_interface')
    expert_interface_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_expert_rating_page')))

    # print("Skipping tutorial")
    # skip_tutorial_btn = driver.find_element_by_id('start_comparing_button')
    # skip_tutorial_btn.click()

    def process_video_selector(vid):
        """Load new video."""

        print("Processing selector", vid)

        # refreshing videos
        selector = driver.find_element_by_id(vid)

        print("Requesting new video...")
        selector.find_element_by_class_name('new_video_button').click()

    with django_db_blocker.unblock():
        assert ExpertRating.objects.filter(user__user__username=test_username).count() == 0

    for which in ['video-left', 'video-right']:
        for _ in range(5):
            process_video_selector(which)

            WebDriverWait(driver, TIME_WAIT).until(
                EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

            selector = driver.find_element_by_id(which)
            c = selector.find_element_by_class_name('video_id_text_field')
            c = c.find_elements_by_tag_name('input')[0]
            txt = c.get_property('value')
            assert txt

            assert do_api_call_v2(driver, '/expert_ratings/?video=' + txt)['count'] == 0

    # creating some ratings
    for _ in range(10):
        do_api_call_v2(driver, '/expert_ratings/', method=post,
                       json={'video_1': shortuuid.ShortUUID().random(length=10),
                             'video_2': shortuuid.ShortUUID().random(length=10),
                             **{k: 50 for k in VIDEO_FIELDS}})

    for which in ['video-left', 'video-right']:
        for _ in range(5):
            process_video_selector(which)

            WebDriverWait(driver, TIME_WAIT).until(
                EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

            selector = driver.find_element_by_id(which)
            c = selector.find_element_by_class_name('video_id_text_field')
            c = c.find_elements_by_tag_name('input')[0]
            txt = c.get_property('value')
            assert txt

            assert do_api_call_v2(driver, '/expert_ratings/?video=' + txt)['count']

    logout(driver)

    cleanup_rate_later(django_db_blocker)


def test_rate_videos(driver, django_db_blocker):
    """Test that we can rate videos."""

    with django_db_blocker.unblock():
        ExpertRating.objects.filter(user__user__username=test_username).delete()

    # fixing the seed for consistent performance
    np.random.seed(41)

    login(driver)

    cleanup_rate_later(django_db_blocker)
    fill_rate_later(django_db_blocker)

    set_all_features_enabled(django_db_blocker)

    print("Going to the expert interface...")
    expert_interface_btn = driver.find_element_by_id('expert_interface')
    expert_interface_btn.click()

    # print("Skipping tutorial")
    # skip_tutorial_btn = driver.find_element_by_id('start_comparing_button')
    # skip_tutorial_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_expert_rating_page')))

    def process_video_selector(vid):
        """Load new video."""

        print("Processing selector", vid)

        # refreshing videos
        selector = driver.find_element_by_id(vid)

        print("Requesting new video...")
        selector.find_element_by_class_name('new_video_button').click()

    v1_id, v2_id = None, None

    # 10 attempts should be enough
    for i in range(10):
        print("Video request attempt", i)
        process_video_selector('video-left')

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

        process_video_selector('video-right')

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

        url_v1_v2 = driver.current_url
        assert url_v1_v2.startswith(web_url)
        url_v1_v2_split = url_v1_v2[len(web_url):].split('/')
        assert len(url_v1_v2_split) == 4
        assert url_v1_v2_split[0] == ''
        assert url_v1_v2_split[1] == 'rate'
        v1_id, v2_id = url_v1_v2_split[2:]
        if v1_id != v2_id:
            break

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    assert v1_id != v2_id, "Video IDs are the same after 10 attempts {v1_id} {v2_id}"
    print("Got videos", v1_id, v2_id)

    np.random.seed(45)
    values = np.random.rand(len(VIDEO_FIELDS)) * 100
    print("Will send values", values)

    for k, v in zip(VIDEO_FIELDS, values):
        set_slider_value(driver, s_id='slider_expert_' + k, value=0)
        set_slider_value(driver, s_id='slider_expert_' + k, value=v)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    print("Submitting the rating...")
    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_submitted_text_info')))

    print("Checking the rating in the database...")
    registered_ratings = do_api_call_v2(driver, url=f"/expert_ratings/?username={test_username}")[
        'results']

    def rating_is_match(r):
        """Is a given rating dict a match to the created one?"""
        if r['username'] != test_username:
            return False
        if r['video_1'] != v1_id:
            return False
        if r['video_2'] != v2_id:
            return False
        for i, f in enumerate(VIDEO_FIELDS):
            if np.abs(r[f] - values[i]) > 1:
                return False
        return True

    assert any([rating_is_match(r) for r in registered_ratings]), \
        f"No matching ratings found in the database, creation failed {v1_id} " \
        f"{v2_id} {values} {registered_ratings}"

    # editing the rating
    np.random.seed(46)
    values = np.random.rand(len(VIDEO_FIELDS)) * 100
    print("Will send edited values", values)

    print("Editing rating...")
    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    for k, v in zip(VIDEO_FIELDS, values):
        set_slider_value(driver, s_id='slider_expert_' + k, value=0)
        set_slider_value(driver, s_id='slider_expert_' + k, value=v)

    print("Submitting the edited rating...")
    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_submitted_text_info')))

    print("Checking the new rating in the database...")
    registered_ratings = do_api_call_v2(driver, url=f"/expert_ratings/?"
                                                    f"username={test_username}")['results']

    assert any([rating_is_match(r) for r in registered_ratings]), \
        f"No matching ratings found in the database, EDITING failed {v1_id} {v2_id} {values} " \
        f"{registered_ratings}"

    with django_db_blocker.unblock():
        assert ExpertRatingSliderChanges.objects.filter(context='RATE').count() > 0

    logout(driver)

    cleanup_rate_later(django_db_blocker)


def test_skipped_videos(driver, django_db_blocker):
    """Test that we can rate videos."""

    cleanup_rate_later(django_db_blocker)

    # fixing the seed for consistent performance
    np.random.seed(41)

    login(driver)
    set_all_features_enabled(django_db_blocker)

    print("Going to the expert interface...")
    expert_interface_btn = driver.find_element_by_id('expert_interface')
    expert_interface_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_expert_rating_page')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_sample_no_video')))

    with django_db_blocker.unblock():
        my_prefs = UserPreferences.objects.get(user__username=test_username)
        ExpertRating.objects.filter(user=my_prefs).delete()
        VideoSelectorSkips.objects.filter(user=my_prefs).delete()

        # ratings
        videos = [Video.objects.create(video_id=random_alphanumeric()) for _ in range(3)]
        [VideoRateLater.objects.create(user=my_prefs, video=v) for v in videos]

    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_expert_rating_page')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert_video')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    def process_video_selector(vid):
        """Load new video."""

        print("Processing selector", vid)

        # refreshing videos
        selector = driver.find_element_by_id(vid)

        print("Requesting new video...")
        selector.find_element_by_class_name('new_video_button').click()

    v1_hist = []
    v2_hist = []

    def get_v1_v2():
        url_v1_v2 = driver.current_url
        assert url_v1_v2.startswith(web_url)
        url_v1_v2_split = url_v1_v2[len(web_url):].split('/')
        assert len(url_v1_v2_split) == 4
        assert url_v1_v2_split[0] == ''
        assert url_v1_v2_split[1] == 'rate'
        v1_id, v2_id = url_v1_v2_split[2:]
        return v1_id, v2_id

    v1_id, v2_id = get_v1_v2()
    v1_hist.append(v1_id)
    v2_hist.append(v2_id)

    i = 0
    while i < 5 or v1_id == v2_id:
        print("Video request attempt", i)
        process_video_selector('video-left')
        process_video_selector('video-right')

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

        v1_id, v2_id = get_v1_v2()
        v1_hist.append(v1_id)
        v2_hist.append(v2_id)
        i += 1
    assert v1_id != v2_id, "Video IDs are the same after 10 attempts {v1_id} {v2_id}"

    print("Submitting the rating...")
    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    # now must have skipped videos
    with django_db_blocker.unblock():
        v1_hist_filtered = list(filter(
            lambda x: get_object_or_None(Video, video_id=x) is not None, v1_hist))[:-1]
        v2_hist_filtered = list(filter(
            lambda x: get_object_or_None(Video, video_id=x) is not None, v2_hist))[:-1]

        skips = filter_object_with_timeout(
            VideoSelectorSkips, user=my_prefs,
            min_count=len(v1_hist_filtered) + len(v2_hist_filtered)) \
            .order_by('datetime_add').values('video__video_id')
        skips = [x['video__video_id'] for x in skips]
        # valid videos all but last one
        print(skips)
        print(v1_hist_filtered)
        print(v2_hist_filtered)

        def array_levenstein(a, b):
            all_values = list(set(a).union(set(b)))
            assert len(all_values) < 27
            value_map = {v: string.ascii_lowercase[i] for (i, v) in enumerate(all_values)}
            a_mapped = ''.join([value_map[t] for t in a])
            b_mapped = ''.join([value_map[t] for t in b])

            print(a_mapped, b_mapped)

            return editdistance.eval(str(a_mapped), str(b_mapped))

        d1 = array_levenstein(v1_hist_filtered + v2_hist_filtered, skips)
        d2 = array_levenstein(v2_hist_filtered + v1_hist_filtered, skips)

        assert d1 <= 1 or d2 <= 1, (d1, d2)

    logout(driver)

    with django_db_blocker.unblock():
        ExpertRating.objects.filter(user=my_prefs).delete()
        VideoSelectorSkips.objects.filter(user=my_prefs).delete()

    cleanup_rate_later(django_db_blocker)


def test_settings(driver, django_db_blocker):
    """Test expert interface settings."""

    # resetting user preferences
    with django_db_blocker.unblock():
        UserPreferences.objects.filter(user__username=test_username).delete()

    # opening settings...
    login(driver)
    print("Going to the expert interface...")
    expert_interface_btn = driver.find_element_by_id('expert_interface')
    expert_interface_btn.click()

    # will load this data to the form...
    data1 = {
        f'{f}_enabled': np.random.choice([True, False])
        for f in VIDEO_FIELDS
    }
    data1['rating_mode'] = 'enable_all'

    data2 = {
        f'{f}_enabled': np.random.choice([True, False])
        for f in VIDEO_FIELDS
    }
    data2['rating_mode'] = 'skip'

    data3 = {
        f'{f}_enabled': np.random.choice([True, False])
        for f in VIDEO_FIELDS
    }
    data3['rating_mode'] = 'confidence'

    def compare_data_with_db(data):
        with django_db_blocker.unblock():
            db_data = UserPreferences.objects.get(user__username=test_username)
        for key, val in data.items():
            assert getattr(db_data, key) == val, (key, getattr(db_data, key), val)

    def compare_form_with_db():

        form_data = {}
        for f in VIDEO_FIELDS:
            WebDriverWait(driver, TIME_WAIT).until(
                EC.presence_of_element_located((By.ID, f'id_checkbox_{f}_enabled')))
            v = driver.find_element_by_id(f'id_checkbox_{f}_enabled').get_property('checked')
            form_data[f + "_enabled"] = v
        opts = ['enable_all', 'skip', 'confidence']
        is_checked = [driver.find_element_by_id('id_' + opt).get_property('checked')
                      for opt in opts]
        assert sum(is_checked) == 1
        form_data['rating_mode'] = opts[is_checked.index(True)]

        compare_data_with_db(form_data)

    def set_form_data(data):
        driver.find_element_by_id("id_" + data['rating_mode']).click()
        for f in VIDEO_FIELDS:
            WebDriverWait(driver, TIME_WAIT).until(
                EC.presence_of_element_located((By.ID, f'id_checkbox_{f}_enabled')))
            elem = driver.find_element_by_id(f'id_checkbox_{f}_enabled')
            if elem.get_property('checked') != data[f + "_enabled"]:
                elem.click()

    for data in [data1, data2, data3]:
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_rating_settings')))

        driver.find_element_by_id('id_rating_settings').click()

        # waiting for the form
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_state_expert_settings_form')))

        compare_form_with_db()

        # setting data
        set_form_data(data)

        # saving data
        driver.find_element_by_id('id_expert_settings_submit').click()

        # waiting for success
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_expert_settings_ok')))

        compare_data_with_db(data)
        compare_form_with_db()

        # closing the form
        driver.find_element_by_id('id_close_settings_form').click()

    logout(driver)


def check_feature_visibility(up, driver):
    """Check that features are displayed correctly (turned on and off)."""
    # checking feature visibility
    for f in VIDEO_FIELDS:
        correct_visibility = getattr(up, f"{f}_enabled")

        if correct_visibility:
            WebDriverWait(driver, TIME_WAIT).until(
                EC.presence_of_element_located((By.ID, 'id_container_feature_' + f)))
        else:
            WebDriverWait(driver, TIME_WAIT).until(
                EC.invisibility_of_element_located((By.ID, 'id_container_feature_' + f)))


def test_rate_enable_all_weight_none(driver, django_db_blocker):
    """Test all features enabled mode."""

    login(driver)

    with django_db_blocker.unblock():
        # creating two videos
        video_1_id = create_test_video()
        video_2_id = create_test_video()

        # setting user preferences
        up = UserPreferences.objects.get(user__username=test_username)

        # disabling all features, except for the first one
        setattr(up, f"{VIDEO_FIELDS[0]}_enabled", True)
        for f in VIDEO_FIELDS[1:]:
            setattr(up, f"{f}_enabled", False)

        # setting mode to enable_all
        up.rating_mode = "enable_all"

        up.save()

    driver.get(web_url + f'/rate/{video_1_id}/{video_2_id}')

    # waiting for the page to load
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    check_feature_visibility(up, driver)

    print("Submitting the rating...")
    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    with django_db_blocker.unblock():
        obj = get_object_with_timeout(ExpertRating, video_1__video_id=video_1_id,
                                      video_2__video_id=video_2_id,
                                      user__user__username=test_username)

        # checking that weights are 1 for the first feature and 0 for the rest
        for i, f in enumerate(VIDEO_FIELDS):
            val = 1.0 if (i == 0) else 0.0
            assert getattr(obj, f"{f}_weight") == val

        # now, setting first value to None
        # and first weight to None

        setattr(obj, VIDEO_FIELDS[0], None)
        setattr(obj, VIDEO_FIELDS[0] + "_weight", 0.0)
        obj.save()

    # editing the rating with default None values and wrong weights
    driver.refresh()

    print(video_1_id, video_2_id)

    # waiting for the page to load
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    print("Submitting the rating...")
    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    with django_db_blocker.unblock():
        obj = get_object_with_timeout(ExpertRating, video_1__video_id=video_1_id,
                                      video_2__video_id=video_2_id,
                                      user__user__username=test_username,
                                      **{VIDEO_FIELDS[0] + "_weight__gt": 0.5})

        # checking that weights are 1 for the first feature and 0 for the rest
        for i, f in enumerate(VIDEO_FIELDS):
            val = 1.0 if (i == 0) else 0.0
            assert getattr(obj, f"{f}_weight") == val

        assert getattr(obj, VIDEO_FIELDS[0]) is not None

    with django_db_blocker.unblock():
        Video.objects.filter(video_id__in=[video_1_id, video_2_id]).delete()

    logout(driver)


def test_rate_skips(driver, django_db_blocker):
    """Test skips mode."""

    login(driver)

    with django_db_blocker.unblock():
        # creating two videos
        video_1_id = create_test_video()
        video_2_id = create_test_video()

        # setting user preferences
        up = UserPreferences.objects.get(user__username=test_username)

        # enabling two features
        for f in VIDEO_FIELDS[:2]:
            setattr(up, f"{f}_enabled", True)
        for f in VIDEO_FIELDS[2:]:
            setattr(up, f"{f}_enabled", False)

        f0, f1 = VIDEO_FIELDS[:2]

        # setting mode to enable_all
        up.rating_mode = "skip"

        up.save()

    driver.get(web_url + f'/rate/{video_1_id}/{video_2_id}')

    # waiting for the page to load
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    check_feature_visibility(up, driver)

    # checkboxes should be unchecked
    elem0 = driver.find_element_by_id("id_checkbox_skip_" + f0)
    elem1 = driver.find_element_by_id("id_checkbox_skip_" + f1)
    assert elem0.get_property('checked') is False
    assert elem1.get_property('checked') is False

    elem1.click()

    print("Submitting the rating...")
    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    with django_db_blocker.unblock():
        obj = get_object_with_timeout(ExpertRating, video_1__video_id=video_1_id,
                                      video_2__video_id=video_2_id,
                                      user__user__username=test_username)

        # checking that weights are 1 for the first feature and 0 for the rest
        for i, f in enumerate(VIDEO_FIELDS):
            val = 1.0 if (i == 0) else 0.0
            assert getattr(obj, f"{f}_weight") == val

        # now, setting first value to None

        setattr(obj, VIDEO_FIELDS[0], None)
        obj.save()

    # editing the rating with default None values and wrong weights
    driver.refresh()

    # waiting for the page to load
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    elem0 = driver.find_element_by_id("id_checkbox_skip_" + f0)
    elem1 = driver.find_element_by_id("id_checkbox_skip_" + f1)
    assert elem0.get_property('checked') is True
    assert elem1.get_property('checked') is True

    print("Submitting the rating...")
    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    with django_db_blocker.unblock():
        obj = get_object_with_timeout(ExpertRating, video_1__video_id=video_1_id,
                                      video_2__video_id=video_2_id,
                                      user__user__username=test_username,
                                      **{VIDEO_FIELDS[0] + "_weight__lte": 0.5})

        # checking that weights are 1 for the first feature and 0 for the rest
        for i, f in enumerate(VIDEO_FIELDS):
            assert getattr(obj, f"{f}_weight") == 0.0

        assert getattr(obj, VIDEO_FIELDS[0]) is not None

    with django_db_blocker.unblock():
        Video.objects.filter(video_id__in=[video_1_id, video_2_id]).delete()

    logout(driver)


def elem_force_click_middle(driver, elem):
    """Do a forced click in the middle of an element."""
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(elem, elem.rect['width'] / 2, elem.rect['height'] / 2)
    action.click()
    action.perform()


def stars_set_value(driver, prefix_id, value_stars, max_stars=3):
    """Set the value of Material UI Rating component."""
    assert value_stars >= 0 and value_stars <= max_stars
    assert isinstance(value_stars, int)
    print("Set stars", prefix_id, value_stars)

    def get_checked(val_item):
        elem_id = prefix_id + "-" + str(val_item)

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, elem_id)))

        elem_inp = driver.find_element_by_id(elem_id)
        val = elem_inp.get_property('checked')
        print("Stars", prefix_id, val_item, elem_id, val)
        return val

    items_checked = [get_checked(v) for v in range(1, max_stars + 1)]

    def click_star(val_item):
        elem_id = prefix_id + "-" + str(val_item)

        label_elem_xpath = f"//label[@for='{elem_id}']"

        print("Click star", prefix_id, val_item, elem_id, label_elem_xpath)

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.XPATH, label_elem_xpath)))

        WebDriverWait(driver, TIME_WAIT).until(
            EC.element_to_be_clickable((By.XPATH, label_elem_xpath)))

        elem = driver.find_element_by_xpath(label_elem_xpath)
        elem.click()

    # if there are any stars enabled, disabling them...
    if any(items_checked):
        click_star(items_checked.index(True) + 1)

    # now, clicking on the correct star
    if value_stars >= 1:
        click_star(value_stars)


def test_rate_confidence(driver, django_db_blocker):
    """Test skips mode."""

    login(driver)

    with django_db_blocker.unblock():
        # creating two videos
        video_1_id = create_test_video()
        video_2_id = create_test_video()

        # setting user preferences
        up = UserPreferences.objects.get(user__username=test_username)

        # enabling two features
        for f in VIDEO_FIELDS[:4]:
            setattr(up, f"{f}_enabled", True)
        for f in VIDEO_FIELDS[4:]:
            setattr(up, f"{f}_enabled", False)

        f0, f1 = VIDEO_FIELDS[:2]

        # setting mode to enable_all
        up.rating_mode = "confidence"

        up.save()

    driver.get(web_url + f'/rate/{video_1_id}/{video_2_id}')

    # waiting for the page to load
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    check_feature_visibility(up, driver)

    # setting stars
    stars_set_value(driver, VIDEO_FIELDS[0] + "_confidence", 0)
    stars_set_value(driver, VIDEO_FIELDS[1] + "_confidence", 1)
    stars_set_value(driver, VIDEO_FIELDS[2] + "_confidence", 2)
    stars_set_value(driver, VIDEO_FIELDS[3] + "_confidence", 3)

    print("Submitting the rating...")
    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    with django_db_blocker.unblock():
        obj = get_object_with_timeout(ExpertRating, video_1__video_id=video_1_id,
                                      video_2__video_id=video_2_id,
                                      user__user__username=test_username)

        # checking weight
        assert getattr(obj, f"{VIDEO_FIELDS[0]}_weight") == 0.0
        assert getattr(obj, f"{VIDEO_FIELDS[1]}_weight") == 0.5
        assert getattr(obj, f"{VIDEO_FIELDS[2]}_weight") == 1.0
        assert getattr(obj, f"{VIDEO_FIELDS[3]}_weight") == 1.5
        for f in VIDEO_FIELDS[4:]:
            assert getattr(obj, f"{f}_weight") == 0.0

        # now, setting second value to None
        setattr(obj, VIDEO_FIELDS[1], None)
        obj.save()

    # editing the rating with default None values and wrong weights
    driver.refresh()

    # waiting for the page to load
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    print("Submitting the rating...")
    expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
    expert_submit_btn.click()

    with django_db_blocker.unblock():
        obj = get_object_with_timeout(ExpertRating, video_1__video_id=video_1_id,
                                      video_2__video_id=video_2_id,
                                      user__user__username=test_username,
                                      **{VIDEO_FIELDS[0] + "_weight__lte": 0.5})

        # checking that weights are 1 for the first feature and 0 for the rest
        assert getattr(obj, f"{VIDEO_FIELDS[0]}_weight") == 0.0
        assert getattr(obj, f"{VIDEO_FIELDS[1]}_weight") == 0.0
        assert getattr(obj, f"{VIDEO_FIELDS[2]}_weight") == 1.0
        assert getattr(obj, f"{VIDEO_FIELDS[3]}_weight") == 1.5
        for f in VIDEO_FIELDS[4:]:
            assert getattr(obj, f"{f}_weight") == 0.0

        assert getattr(obj, VIDEO_FIELDS[0]) is not None

    with django_db_blocker.unblock():
        Video.objects.filter(video_id__in=[video_1_id, video_2_id]).delete()

    logout(driver)


def test_feature_links(driver, django_db_blocker):
    login(driver)

    set_all_features_enabled(django_db_blocker)

    print("Going to the expert interface...")
    expert_interface_btn = driver.find_element_by_id('expert_interface')
    expert_interface_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_expert_rating_page')))

    for f in VIDEO_FIELDS:
        elem_id = "id_explanation_" + f

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, elem_id)))

        link = driver.find_element_by_id(elem_id).get_attribute('href')
        assert link.startswith('http'), link

        resp = get(link)
        assert resp.ok
        assert resp.status_code == 200
        assert 'MediaWiki' in resp.text

        print(f, resp.text[:500])

    logout(driver)


def test_only_default_enabled(driver, django_db_blocker):
    with django_db_blocker.unblock():
        UserPreferences.objects.filter(user__username=test_username).delete()

    login(driver)

    with django_db_blocker.unblock():
        up = UserPreferences.objects.get(user__username=test_username)

    print("Going to the expert interface...")
    expert_interface_btn = driver.find_element_by_id('expert_interface')
    expert_interface_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_expert_rating_page')))

    for f in VIDEO_FIELDS:
        assert featureIsEnabledByDeFault[f] == getattr(up, f + "_enabled")

    check_feature_visibility(up, driver)
    logout(driver)


def test_insert_video_id(driver, django_db_blocker):
    """Test that we can insert videos into the Video ID field in VideoSelector."""

    cleanup_rate_later(django_db_blocker)
    set_all_features_enabled(django_db_blocker)

    # format: text to insert -> resulting stored ID or None if no record should exist
    ids_to_insert = {
        'https://www.youtube.com/watch?v=gU-mkuMU428&ab_channel=LexFridman':
            'gU-mkuMU428',
        'https://youtu.be/gU-mkuMU428': 'gU-mkuMU428',
        'https://www.youtube.com/embed/gU-mkuMU428': 'gU-mkuMU428',
        'gU-mkuMU428': 'gU-mkuMU428',
        '@@@-': '-',
        'ghslkdfjghklsdjfghksldjfdskljfghskdljfghlskdjfghsldkfjghsldkfjghsfldgjkshdlkfg':
            'ghslkdfjghklsdjfghks',
        '$$$$$????++++-': '-',
        '| rm -rf / ': 'rm-rf',
        '"""-': '-'
    }

    login(driver)

    print("Going to the expert interface...")
    expert_interface_btn = driver.find_element_by_id('expert_interface')
    expert_interface_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_expert_rating_page')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

    def get_input_elem(vid):
        """Get the input element for a video selector."""
        print("Processing selector", vid)

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, vid)))

        # refreshing videos
        selector = driver.find_element_by_id(vid)

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'video_id_text_field')))

        print("Obtaining element...")
        elem = selector.find_element_by_class_name('video_id_text_field')
        elem = elem.find_element_by_tag_name('input')

        return elem

    # creating the left video
    with django_db_blocker.unblock():
        video_id_left = create_test_video()

    def process_video_selector(vid, video_enter):
        """Load new video."""
        elem = get_input_elem(vid)
        elem.clear()
        clipboard.copy(video_enter)
        print("Copying text", video_enter, "into", vid)
        elem.send_keys(Keys.LEFT_CONTROL, "v")

    for text_enter, resulting_id in ids_to_insert.items():
        with django_db_blocker.unblock():
            ExpertRating.objects.filter(user__user__username=test_username).delete()

        print("Entering", text_enter, "expecting", resulting_id)

        process_video_selector('video-left', video_id_left)

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

        process_video_selector('video-right', text_enter)

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

        print("Submitting the rating...")
        expert_submit_btn = driver.find_element_by_id('expert_submit_btn')
        expert_submit_btn.click()

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_no_pending_expert')))

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_no_pending_submit')))

        if resulting_id is not None:
            with django_db_blocker.unblock():
                get_object_with_timeout(ExpertRating, video_1__video_id=video_id_left,
                                        video_2__video_id=resulting_id,
                                        user__user__username=test_username)
        else:
            with django_db_blocker.unblock():
                assert ExpertRating.objects.filter(user__user__username=test_username).count() == 0

    logout(driver)
