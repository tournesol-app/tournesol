import os
import pickle
from io import StringIO
from uuid import uuid1

import numpy as np
from backend.models import DjangoUser
from backend.models import UserInformation
from backend.models import VerifiableEmail, Expertise, ExpertiseKeyword, Degree, EmailDomain
from django_react.settings import BASE_DIR
from django_react.settings import EMAIL_PAGE_DOMAIN
from helpers import get_last_email, test_username, do_api_call_v2, get_cookies, get, \
    random_alphanumeric, TIME_WAIT
from helpers import login, logout, web_url
from lxml import html
from matplotlib import pyplot as plt
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_user_profile_navigate(driver, django_db_blocker):
    """Test that going from another person's profile to mine works, see #309."""
    with django_db_blocker.unblock():
        other_username = random_alphanumeric()
        u = DjangoUser.objects.create_user(username=other_username)
        print(other_username)

    login(driver)

    with django_db_blocker.unblock():
        UserInformation.objects.filter(user__username=test_username)\
            .update(first_name='Selenium')
        UserInformation.objects.filter(user__username=other_username)\
            .update(first_name='Other user')

    driver.get(web_url + '/user/' + other_username)

    def current_profile_first_name():
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, "id_user_page_loaded")))

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, "id_first_last_name_certified_user")))

        result = driver.find_element_by_id('id_first_last_name_certified_user').text
        print('firstname', result)
        return result

    assert current_profile_first_name().startswith('Other user')

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "personal_info_menu")))

    driver.find_element_by_id('personal_info_menu').click()

    assert current_profile_first_name().startswith('Selenium')

    with django_db_blocker.unblock():
        u.delete()

    logout(driver)


def test_no_show(driver, django_db_blocker):
    login(driver)

    with django_db_blocker.unblock():
        username = "aba" + str(uuid1())
        u = DjangoUser.objects.create_user(username=username)
        ui = UserInformation.objects.create(user=u, show_my_profile=False)

    r = do_api_call_v2(driver=driver, url=f'/user_information/{ui.id}/', expect_fail=True)
    assert not r.ok

    r = do_api_call_v2(driver=driver, url=f'/user_information/?user__username={username}')
    assert r['count'] == 0

    # test that can see my own hidden profile
    with django_db_blocker.unblock():
        UserInformation.objects.filter(user__username=test_username).update(show_my_profile=False)

    r = do_api_call_v2(driver=driver, url=f'/user_information/?user__username={test_username}')
    assert r['count'] == 1

    with django_db_blocker.unblock():
        UserInformation.objects.filter(user__username=test_username).update(show_my_profile=True)

    logout(driver)
    with django_db_blocker.unblock():
        u.delete()


def test_privacy(driver, django_db_blocker):
    login(driver)

    # privacy test
    # creating a temp user
    with django_db_blocker.unblock():
        u = DjangoUser.objects.create_user(username="aba" + str(uuid1()))
        ui = UserInformation.objects.create(user=u)

    def check_sensitive(res):
        assert 'gender' not in res
        assert 'race' not in res
        assert 'emails' not in res
        assert 'nationality' not in res
        assert 'residence' not in res
        assert 'moral_philosophy' not in res
        assert 'political_affiliation' not in res
        assert 'degree_of_political_engagement' not in res
        assert 'religion' not in res

    with django_db_blocker.unblock():
        ui.show_online_presence = True
        ui.save()

    res = do_api_call_v2(driver=driver, url=f'/user_information/{ui.id}/')
    check_sensitive(res)

    for x in ['google_scholar', 'website', 'linkedin', 'orcid',
              'twitter', 'youtube', 'researchgate']:
        assert x in res

    with django_db_blocker.unblock():
        ui.show_online_presence = False
        ui.save()
    res = do_api_call_v2(driver=driver, url=f'/user_information/{ui.id}/')
    check_sensitive(res)

    for x in ['google_scholar', 'website', 'linkedin', 'orcid',
              'twitter', 'youtube', 'researchgate']:
        assert x not in res

    with django_db_blocker.unblock():
        u.delete()

    logout(driver)


def userprofile_set_data(driver, form):
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_userinformation_form")))

    # setting data
    for key, val in form.items():
        if isinstance(val, (str, bool, tuple)):
            elems = driver.find_elements_by_name('root_' + key)
            elem = None
            if len(elems) == 1:
                elem = elems[0]
                # print('wait by name', 'root_' + key)
                # WebDriverWait(driver, TIME_WAIT).until(
                #     EC.element_to_be_clickable((By.NAME, 'root_' + key))
                # )
            if not elem:
                elems = driver.find_elements_by_id('root_' + key)
                if len(elems) == 1:
                    elem = elems[0]
                    # print('wait by id', 'root_' + key)
                    # WebDriverWait(driver, TIME_WAIT).until(
                    #     EC.element_to_be_clickable((By.ID, 'root_' + key))
                    # )
            #
            # print('wait clickable', key)
            # WebDriverWait(driver, TIME_WAIT).until(
            #     EC.visibility_of(elem))

        if isinstance(val, str):
            elem.clear()
            elem.send_keys(val)
        elif isinstance(val, bool):
            if elem.get_property('checked') != val:
                elem.click()
        elif isinstance(val, tuple):
            val = val[0]
            elem.click()
            opts = [x for x in driver.find_elements_by_tag_name('li') if x.text == val]
            assert len(opts) == 1, opts
            opts[0].click()

            WebDriverWait(driver, TIME_WAIT).until(
                EC.invisibility_of_element(opts[0])
            )

        elif isinstance(val, list):
            h5s = [x for x in driver.find_elements_by_tag_name('h5') if
                   x.text.lower().replace(' ', '_').replace('e-mails', 'emails') == key]
            assert len(h5s) == 1, (key, h5s)

            # deleting everything
            for _ in range(10):
                buttons_plus = h5s[0].find_element_by_xpath('./../..')\
                    .find_elements_by_tag_name('button')

                print(buttons_plus[0])

                if len(buttons_plus) >= 3:
                    idx = 2
                    if 'expertise' in key.lower():
                        idx = -2
                    buttons_plus[idx].click()  # deleting some
                    continue

                elif len(buttons_plus) > 1:
                    idx = 0
                    if 'expertise' in key.lower():
                        idx = -1
                    buttons_plus[idx].click()
                    continue

                elif len(buttons_plus) == 1:

                    # assert len(buttons_plus) >= 1
                    button_plus = buttons_plus[-1]
                    break

            # adding items
            for _ in range(len(val)):
                button_plus.click()

            # filling data
            for i, dct in enumerate(val):
                for key_, val_ in dct.items():
                    f = driver.find_element_by_id(f'root_{key}_{i}_{key_}')
                    f.click()
                    f.clear()
                    f.send_keys(val_)


def userprofile_submit(driver, do_check_ok=True):
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_userinfo_submit")))

    submit_buttons = [x for x in driver.find_elements_by_tag_name('button') if
                      x.get_attribute('type') == 'submit']
    assert len(submit_buttons) == 1
    submit_buttons[0].click()

    def check_submit_ok():
        alerts = driver.find_elements_by_class_name('class_success_data_save')
        assert len(alerts) == 1

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "class_data_save")))
    if do_check_ok:
        check_submit_ok()


def userprofile_check_data(django_db_blocker, form, test_img=None):
    # checking data
    with django_db_blocker.unblock():
        uinf = UserInformation.objects.get(user__username=test_username)
        uinf.refresh_from_db()

    for key, val in form.items():
        if key == 'avatar':
            f_true = open(test_img, 'rb').read()
            with django_db_blocker.unblock():
                f_uploaded = uinf.avatar.read()
            assert f_true == f_uploaded
        elif isinstance(val, list):
            with django_db_blocker.unblock():
                val_db = getattr(uinf, key).all()
                assert len(val) == len(val_db)
                for item, item_db in zip(val, val_db):
                    for key in item:
                        assert item[key] == getattr(item_db, key)

        else:
            if isinstance(val, tuple):
                val = val[0]
            true_val = getattr(uinf, key)
            if true_val is None:
                true_val = ""
            assert str(true_val) == str(val), key


def test_data_save(driver, django_db_blocker):
    # deleting old info
    with django_db_blocker.unblock():
        UserInformation.objects.filter(user__username=test_username).delete()

    login(driver)

    driver.find_element_by_id('personal_info_menu').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "edit_userprofile_button_id")))
    driver.find_element_by_id('edit_userprofile_button_id').click()

    # can submit the form without data
    userprofile_submit(driver)

    driver.refresh()
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "edit_userprofile_button_id")))
    driver.find_element_by_id('edit_userprofile_button_id').click()

    # an image
    img = np.random.rand(300, 300, 3)
    test_img = os.path.join(os.getcwd(), 'test_image.png')
    plt.imshow(img)
    plt.savefig(test_img, bbox_inches='tight')

    test_non_image = os.path.join(os.getcwd(), 'data_file.pkl')
    with open(test_non_image, 'wb') as f:
        pickle.dump({1: 'test'}, f)

    form = {
        'comment_anonymously': True,
        'show_online_presence': True,
        'avatar': test_img,
        'first_name': "Test",
        'last_name': "aba",
        'title': "researcher",
        'bio': 'and a \nmagician',
        'birth_year': "1984",
        'nationality': ('Russia',),
        'residence': ('Switzerland',),
        'moral_philosophy': ('Utilitarian',),
        'google_scholar': 'http://scholar.google.com/abas',
        'website': "http://magic.org",
        'linkedin': 'http://www.linkedin.com/abal',
        'orcid': 'http://orcid.org/abao',
        'researchgate': 'http://researchgate.net/abar',
        'twitter': 'http://twitter.com/abat',
        'youtube': 'http://www.youtube.com/abay',
        'gender': ("Male",),
        'race': ("African",),
        'political_affiliation': ("Left",),
        'degree_of_political_engagement': ("Light",),
        'religion': ("Atheist",),

        'expertises': [{'name': "aba"}, {'name': 'caba'}],
        'expertise_keywords': [{'name': "aba123"}, {'name': 'cabaxxx'}],
        'degrees': [{'level': 'MSc', 'institution': "mit", 'domain': "Applied Magic"}],
        'emails': [{'email': 'xyz@aba.com'}]
    }

    form_empty = {
        'comment_anonymously': True,
        'show_online_presence': True,
        'avatar': test_img,
        'first_name': "",
        'last_name': "",
        'title': "",
        'bio': '',
        'birth_year': "",
        'nationality': ('Not Specified',),
        'residence': ('Not Specified',),
        'moral_philosophy': ('Not Specified',),
        'google_scholar': '',
        'researchgate': '',
        'website': "",
        'linkedin': '',
        'orcid': '',
        'twitter': '',
        'youtube': '',
        'gender': ("Not Specified",),
        'race': ("Not Specified",),
        'political_affiliation': ("Not Specified",),
        'degree_of_political_engagement': ("Not Specified",),
        'religion': ("Not Specified",),

        'expertises': [],
        'expertise_keywords': [],
        'degrees': [],
        'emails': [],
    }

    form_errors = {
        'comment_anonymously': True,
        'show_online_presence': True,
        'avatar': test_non_image,
        'first_name': "Test",
        'last_name': "aba",
        'title': "researcher",
        'bio': 'and a \nmagician',
        'birth_year': "3010",
        'nationality': ('Russia',),
        'residence': ('Switzerland',),
        'moral_philosophy': ('Utilitarian',),
        'google_scholar': 'httpzz://xyz.com',
        'website': "httpzz://magic.org",
        'linkedin': 'httpzz://aasdasd.com',
        'orcid': 'httpzz://123.com',
        'researchgate': 'httpzz://123rg.com',
        'twitter': 'httpxx://twitter.com',
        'youtube': 'httpxx://yt.com',
        'gender': ("Male",),
        'race': ("Caucasian",),
        'political_affiliation': ("Left",),
        'degree_of_political_engagement': ("None",),
        'religion': ("Atheist",),

        'expertises': [{'name': ""}, {'name': 'caba'}],
        'expertise_keywords': [{'name': ""}, {'name': 'cabaxxx'}],
        'degrees': [{'level': 'MSc', 'institution': "", 'domain': "Applied Magic"}],
        'emails': [{'email': ''}]
    }

    # submitting data
    userprofile_set_data(driver, form)
    userprofile_submit(driver)
    userprofile_check_data(django_db_blocker, form, test_img)

    driver.refresh()
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "edit_userprofile_button_id")))
    driver.find_element_by_id('edit_userprofile_button_id').click()

    # submitting empty
    userprofile_set_data(driver, form_empty)
    userprofile_submit(driver)
    userprofile_check_data(django_db_blocker, form_empty, test_img)

    driver.refresh()
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "edit_userprofile_button_id")))
    driver.find_element_by_id('edit_userprofile_button_id').click()

    # submitting form with errors
    # checking that the form does not break
    userprofile_set_data(driver, form_errors)
    userprofile_submit(driver, do_check_ok=False)
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "class_error_data_save")))
    assert driver.find_elements_by_class_name('class_error_data_save')

    driver.refresh()

    os.unlink(test_img)
    os.unlink(test_non_image)
    logout(driver)


def test_data_download(driver, django_db_blocker):
    login(driver)

    driver.find_element_by_id('personal_info_menu').click()
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_my_data_download")))

    link = driver.find_element_by_id('id_my_data_download').get_attribute('href')

    cookies_dict = get_cookies(driver)
    headers = {'X-CSRFToken': cookies_dict.get('csrftoken')}

    data = get(link, cookies=cookies_dict, headers=headers)
    assert data.ok
    assert data.content
    assert data.headers['content-type'] == 'application/zip'

    logout(driver)


def test_user_page(driver, django_db_blocker):
    img = np.random.rand(300, 300, 3)
    test_img = os.path.join(BASE_DIR, 'media', 'profiles', 'test_image.png')
    plt.imshow(img)
    plt.savefig(test_img, bbox_inches='tight')

    login(driver)

    with django_db_blocker.unblock():
        # creating a user with data
        u = DjangoUser.objects.create_user(username=f"u{str(uuid1())}")
        ui = UserInformation.objects.create(user=u)
        accepted_domain = f"@{random_alphanumeric()}.com"
        EmailDomain.objects.create(domain=accepted_domain, status=EmailDomain.STATUS_ACCEPTED)
        VerifiableEmail.objects.create(email=f"{random_alphanumeric()}{accepted_domain}", user=ui,
                                       is_verified=True)

        ui.first_name = "FN"
        ui.last_name = "LN"
        ui.title = "T"
        ui.bio = "B"
        ui.website = "http://aba_w.xyz/"
        ui.orcid = "http://orcid.org/aaao"
        ui.twitter = "http://twitter.com/aaat"
        ui.linkedin = "http://linkedin.com/aaal"
        ui.researchgate = "http://researchgate.net/aaar"
        ui.youtube = "http://youtube.com/aaay"
        ui.google_scholar = "http://scholar.google.com/aaas"
        ui.avatar.name = 'profiles/test_image.png'  # test_img
        ui.show_online_presence = True
        e = Expertise(name="aba")
        ekw = ExpertiseKeyword(name="zzz")
        deg = Degree(level="aa", institution="zzz", domain="magic")
        deg.save()
        ekw.save()
        e.save()
        ui.expertises.set([e])
        ui.expertise_keywords.set([ekw])
        ui.degrees.set([deg])
        ui.save()

    driver.get(web_url + f'/user/{u.username}/')

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_first_last_name_certified_user")))

    # checking that data is valid
    assert driver.find_element_by_id('id_first_last_name_certified_user').text == 'FN LN'
    assert driver.find_element_by_id('id_title_user').text == 'T'
    assert driver.find_element_by_id('id_bio_user').text == 'B'
    assert driver.find_element_by_id('id_website_user').get_attribute('href') == ui.website
    assert driver.find_element_by_id('id_linkedin_user').get_attribute('href') == ui.linkedin
    assert driver.find_element_by_id('id_google_scholar_user').get_attribute(
        'href') == ui.google_scholar
    assert driver.find_element_by_id('id_twitter_user').get_attribute('href') == ui.twitter
    assert driver.find_element_by_id('id_orcid_user').get_attribute('href') == ui.orcid
    assert driver.find_element_by_id('id_researchgate_user')\
           .get_attribute('href') == ui.researchgate
    assert driver.find_element_by_id('id_youtube_user').get_attribute('href') == ui.youtube

    img_src = driver.find_element_by_id('id_profile_user').get_attribute('src')
    assert img_src.startswith('http')

    cookies_dict = get_cookies(driver)
    headers = {'X-CSRFToken': cookies_dict.get('csrftoken')}
    r = get(img_src, cookies=cookies_dict, headers=headers)
    assert r.ok
    with open(test_img, 'rb') as f:
        assert r.content == f.read()

    exps = driver.find_elements_by_class_name('class_expertise_user')
    assert len(exps) == 1, exps
    assert exps[0].text == 'aba'

    exp_kws = driver.find_elements_by_class_name('class_expertise_keyword_user')
    assert len(exp_kws) == 1, exp_kws
    assert exp_kws[0].text == 'zzz'

    degs = driver.find_elements_by_class_name('class_degree_user')
    assert len(degs) == 1, degs
    assert degs[0].text == 'aa, magic, zzz'

    with django_db_blocker.unblock():
        u.delete()

    logout(driver)
    os.unlink(test_img)


def confirm_last_email(driver):
    email_parsed = get_last_email()

    email_payload = None
    for payload in email_parsed.walk():
        print("payload", payload.get_content_type())
        if payload.get_content_type() == 'text/html':
            email_payload = payload.get_payload()
    assert email_payload

    html_parsed = html.parse(StringIO(email_payload))

    # confirming e-mail address
    confirm_link = html_parsed.xpath("//a[@id = 'confirmation_link_id']")[0].get('href')
    confirm_link = confirm_link.replace(EMAIL_PAGE_DOMAIN, 'http://127.0.0.1:8000/')
    print("Navigating to", confirm_link)
    driver.get(confirm_link)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_email_instructions')))


def test_add_email_from_expert_interface(driver, django_db_blocker):
    domains = {'accepted': f"@{random_alphanumeric()}.com",
               'pending': f"@{random_alphanumeric()}.com",
               'rejected': f"@{random_alphanumeric()}.com"}

    emails = {status: f"test{domain}" for status, domain in domains.items()}

    with django_db_blocker.unblock():
        u = DjangoUser.objects.get(username=test_username)
        ui, _ = UserInformation.objects.get_or_create(user=u)
        VerifiableEmail.objects.filter(user=ui).delete()

        for status, domain in domains.items():
            s = getattr(EmailDomain, f'STATUS_{status}'.upper())
            EmailDomain.objects.create(domain=domain, status=s)

    login(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_pending')))

    assert len(driver.find_elements_by_class_name('class_pending')) == 1

    # adding an e-mail
    def form_input(email):
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert_email_class')))
        email_form = driver.find_element_by_class_name(
            'alert_email_class').find_element_by_tag_name('input')
        email_form.clear()
        print("email", email)
        email_form.send_keys(email)
        driver.find_element_by_class_name('alert_email_add_submit').click()
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_add_email_success')))

    form_input(emails['pending'])
    driver.get(web_url)
    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_pending')))

    assert len(driver.find_elements_by_class_name('class_pending')) == 1
    confirm_last_email(driver)

    driver.get(web_url)
    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_pending')))

    assert len(driver.find_elements_by_class_name('class_pending')) == 1

    form_input(emails['rejected'])
    driver.get(web_url)
    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_pending')))

    assert len(driver.find_elements_by_class_name('class_pending')) == 1
    assert len(driver.find_elements_by_class_name('class_rejected')) == 0
    confirm_last_email(driver)

    driver.get(web_url)
    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_rejected')))

    assert len(driver.find_elements_by_class_name('class_rejected')) == 1

    form_input(emails['accepted'])
    driver.get(web_url)
    driver.refresh()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'class_rejected')))

    assert len(driver.find_elements_by_class_name('class_rejected')) == 1
    confirm_last_email(driver)

    driver.get(web_url)
    driver.refresh()
    assert len(driver.find_elements_by_class_name('class_rejected')) == 0
    assert len(driver.find_elements_by_class_name('class_pending')) == 0

    logout(driver)

    with django_db_blocker.unblock():
        for email in emails.values():
            VerifiableEmail.objects.filter(email=email).delete()
