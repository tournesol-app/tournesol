from uuid import uuid1

from backend.models import Video, VideoComment, UserInformation, \
    DjangoUser, EmailDomain, VerifiableEmail, UserPreferences, VideoRatingThankYou, ExpertRating
from helpers import test_username, login, logout, do_api_call_v2, \
    create_test_video, TIME_WAIT, get_object_with_timeout, random_alphanumeric, open_more_menu
from selenium import webdriver
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_comments(driver, django_db_blocker):
    # creating a video

    with django_db_blocker.unblock():
        video_id = create_test_video()

    login(driver)

    open_more_menu(driver)

    with django_db_blocker.unblock():
        UserInformation.objects.filter(user__username=test_username).update(
            comment_anonymously=False)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.visibility_of_element_located((By.ID, 'video_details_menu')))

    print("Going to the details page")
    expert_interface_btn = driver.find_element_by_id('video_details_menu')
    expert_interface_btn.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'video_id_text_field')))

    elem = driver.find_element_by_class_name('video_id_text_field')
    elem = elem.find_element_by_tag_name('input')

    # setting the video ID
    elem.clear()
    elem.send_keys(video_id, Keys.HOME)
    if elem.get_attribute('value') != video_id:
        elem.send_keys(3 * [Keys.DELETE])

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, f'comment_editor_{video_id}_undefined')))

    # sending the comment
    editor = driver.find_element_by_class_name(f'comment_editor_{video_id}_undefined')
    editor.find_element_by_class_name('public-DraftEditor-content').send_keys('sdf')
    driver.find_elements_by_class_name(f'comment_editor_submit_{video_id}_undefined')[0].click()

    # checking results
    with django_db_blocker.unblock():
        comment = get_object_with_timeout(VideoComment, video__video_id=video_id,
                                          parent_comment=None)
        assert comment.comment == "<p>sdf</p>"
        assert not comment.anonymous
        cid = VideoComment.objects.filter(video__video_id=video_id).get().id

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, f'comment_{cid}_reply')))

    # replying to a comment
    driver.find_element_by_class_name(f'comment_{cid}_reply').click()
    driver.find_element_by_class_name(
        f'comment_editor_{video_id}_{cid}').find_element_by_class_name(
        'public-DraftEditor-content').send_keys('aba')
    driver.find_elements_by_class_name(f'comment_editor_submit_{video_id}_{cid}')[0].click()

    with django_db_blocker.unblock():
        subcid = get_object_with_timeout(VideoComment, video__video_id=video_id,
                                         parent_comment__id=cid).id

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, f'comment_{subcid}_reply')))

    # replying to a reply anonymously
    driver.find_element_by_class_name(f'comment_{subcid}_reply').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, f'comment_editor_{video_id}_{subcid}')))

    driver.find_element_by_class_name(
        f'comment_editor_{video_id}_{subcid}').find_element_by_class_name(
        'public-DraftEditor-content').send_keys('zzzaaa')
    checkbox = driver.find_element_by_class_name(
        f'anonymous_comment_checkbox_class_{video_id}_{subcid}')
    if not checkbox.find_element_by_tag_name('input').get_property('checked'):
        checkbox.click()
    driver.find_elements_by_class_name(f'comment_editor_submit_{video_id}_{subcid}')[0].click()

    with django_db_blocker.unblock():
        assert get_object_with_timeout(VideoComment, video__video_id=video_id,
                                       parent_comment__id=cid).comment == '<p>aba</p>'

        subsubc = get_object_with_timeout(VideoComment, video__video_id=video_id,
                                          parent_comment_id=subcid)
        assert subsubc.anonymous
        assert subsubc.comment == '<p>zzzaaa</p>'
    # editing the subcomment
    with django_db_blocker.unblock():
        ecid = get_object_with_timeout(VideoComment, video__video_id=video_id,
                                       parent_comment__id=cid).id

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, f'comment_{ecid}_edit')))

    driver.find_element_by_class_name(f'comment_{ecid}_edit').click()
    elem = driver.find_element_by_class_name(
        f'comment_editor_cid_{ecid}').find_element_by_class_name(
        'public-DraftEditor-content')

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, f'comment_editor_cid_{ecid}_editing'))
    )

    elem.click()
    elem.send_keys('xyz')
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, f'comment_{ecid}_save_edits')))

    driver.find_element_by_class_name(f'comment_{ecid}_save_edits').click()
    with django_db_blocker.unblock():
        assert get_object_with_timeout(VideoComment,
                                       video__video_id=video_id,
                                       parent_comment__id=cid).comment.strip() == '<p>xyzaba</p>'

    # comment markers
    with django_db_blocker.unblock():
        assert VideoComment.objects.filter(video__video_id=video_id,
                                           parent_comment__id=cid).get().votes_plus == 0
    driver.find_element_by_class_name(f'vote_plus_comment_{ecid}').click()
    with django_db_blocker.unblock():
        assert VideoComment.objects.filter(video__video_id=video_id,
                                           parent_comment__id=cid).get().votes_plus == 1
    driver.find_element_by_class_name(f'vote_plus_comment_{ecid}').click()
    with django_db_blocker.unblock():
        assert VideoComment.objects.filter(video__video_id=video_id,
                                           parent_comment__id=cid).get().votes_plus == 0

    logout(driver)


def test_comment_uncertified(driver, django_db_blocker):
    # creating a user and leaving a comment, checking that it is not shown
    username = str(uuid1())
    domain = f"@{uuid1()}.com"

    with django_db_blocker.unblock():
        u = DjangoUser.objects.create_user(username=username, is_active=True)
        EmailDomain.objects.create(domain=domain, status=EmailDomain.STATUS_ACCEPTED)
        ui = UserInformation.objects.create(user=u)
        up = UserPreferences.objects.create(user=u)
        v = Video.objects.create(video_id=random_alphanumeric())
        VerifiableEmail.objects.create(user=ui, email=f"test{domain}")
        VideoComment.objects.create(user=up, video=v, comment="test")

    login(driver)

    res = do_api_call_v2(driver, '/video_comments/?video__video_id=' + v.video_id)
    assert res['count'] == 0

    with django_db_blocker.unblock():
        VerifiableEmail.objects.filter(user=ui, email=f"test{domain}").update(is_verified=True)

    res = do_api_call_v2(driver, '/video_comments/?video__video_id=' + v.video_id)
    assert res['count'] == 1

    logout(driver)

    with django_db_blocker.unblock():
        u.delete()
        v.delete()


def test_mention(driver, django_db_blocker):
    login(driver)

    with django_db_blocker.unblock():
        video_id = create_test_video()
        domain = EmailDomain.objects.create(status=EmailDomain.STATUS_ACCEPTED,
                                            domain="@" + random_alphanumeric() + ".com")
        ve = VerifiableEmail.objects.create(
            user=UserInformation.objects.get(user__username=test_username),
            email="aba" + domain.domain, is_verified=True)

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

    # setting the video ID
    elem.clear()
    elem.send_keys(video_id, Keys.HOME)
    if elem.get_attribute('value') != video_id:
        elem.send_keys(3 * [Keys.DELETE])

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, f'comment_editor_{video_id}_undefined')))

    # sending the comment
    editor = driver.find_element_by_class_name(f'comment_editor_{video_id}_undefined')
    editor.find_element_by_class_name('public-DraftEditor-content').send_keys('@' + test_username)

    # selecting the mention suggestion
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'rdw-suggestion-option')))

    elems = driver.find_elements_by_class_name('rdw-suggestion-option')
    elems = [x for x in elems if test_username in x.text]
    assert len(elems) == 1

    WebDriverWait(driver, TIME_WAIT).until(
        EC.visibility_of(elems[0]))

    elems[0].click()

    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(elems[0], elems[0].rect['width'] / 2,
                                       elems[0].rect['height'] / 2)
    action.click()
    action.perform()
    WebDriverWait(driver, TIME_WAIT).until(
        EC.invisibility_of_element(elems[0]))

    driver.find_elements_by_class_name(f'comment_editor_submit_{video_id}_undefined')[0].click()

    with django_db_blocker.unblock():
        assert get_object_with_timeout(VideoComment, video__video_id=video_id)

    # going to mentions...
    driver.find_element_by_id('personal_info_menu').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_mentions')))

    driver.find_element_by_id('id_mentions').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_li_comment_mention')))

    assert len(driver.find_elements_by_class_name('class_li_comment_mention')) == 1

    logout(driver)

    with django_db_blocker.unblock():
        Video.objects.filter(video_id=video_id).delete()
        ve.delete()


def test_thank_unthank(driver, django_db_blocker):
    with django_db_blocker.unblock():
        video_id = create_test_video()
        video = Video.objects.get(video_id=video_id)

        video_id1 = create_test_video()
        video1 = Video.objects.get(video_id=video_id1)

        domain = EmailDomain.objects.create(status=EmailDomain.STATUS_ACCEPTED,
                                            domain="@" + random_alphanumeric() + ".com")

        # creating a certified user with ratings of the video
        other_user = DjangoUser.objects.create_user(username=random_alphanumeric(),
                                                    is_active=True)
        oup = UserPreferences.objects.create(user=other_user)
        oui = UserInformation.objects.create(user=other_user)

        ExpertRating.objects.create(user=oup, video_1=video,
                                    video_2=video1)

        ve = VerifiableEmail.objects.create(
            user=oui,
            email="aba" + domain.domain, is_verified=True)

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
    elem = elem.find_element_by_tag_name('input')

    # setting the video ID
    elem.clear()
    elem.send_keys(video_id, Keys.HOME)
    if elem.get_attribute('value') != video_id:
        elem.send_keys(3 * [Keys.DELETE])

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, f'id_{video_id}_thank')))

    driver.find_element_by_id(f'id_{video_id}_thank').click()

    with django_db_blocker.unblock():
        assert get_object_with_timeout(VideoRatingThankYou,
                                       video__video_id=video_id,
                                       thanks_from__user__username=test_username,
                                       thanks_to__user__username=other_user.username)
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, f'id_{video_id}_unthank')))

    driver.find_element_by_id(f'id_{video_id}_unthank').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, f'id_{video_id}_thank')))

    with django_db_blocker.unblock():
        assert VideoRatingThankYou.objects.filter(
            video__video_id=video_id, thanks_from__user__username=test_username,
            thanks_to__user__username=other_user.username).count() == 0

    logout(driver)

    with django_db_blocker.unblock():
        Video.objects.filter(video_id=video_id).delete()
        Video.objects.filter(video_id=video_id1).delete()

        ve.delete()
        other_user.delete()
