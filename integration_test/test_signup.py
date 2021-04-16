import secrets
from uuid import uuid1

from backend.models import DjangoUser, UserInformation, VerifiableEmail
from django_react import settings
from helpers import login, logout, web_url, test_password, get_last_email, open_tournesol, \
    test_username, TIME_WAIT
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def signup(driver, django_db_blocker, username, password, email):
    open_tournesol(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "signup_button")))

    # sign up
    driver.find_element_by_id('signup_button').click()

    user_data = {'root_username': username,
                 'root_email': email,
                 'root_password': password,
                 'root_password2': password}

    for key, val in user_data.items():
        elem = driver.find_element_by_id(key)
        elem.clear()
        elem.send_keys(val)

    # accepting the privacy policy
    pp_ckbox = driver.find_element_by_id('root_shrivacy_policy')
    if not pp_ckbox.get_property('checked'):
        pp_ckbox.click()

    buttons = driver.find_elements_by_tag_name('button')
    buttons = [x for x in buttons if x.get_attribute('type') == 'submit']
    assert len(buttons) == 1
    buttons[0].click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_email_instructions')))

    driver.delete_all_cookies()
    driver.get(web_url)

    with django_db_blocker.unblock():
        # manually activating the user
        user = DjangoUser.objects.get(username=user_data['root_username'])
        user.is_active = True
        user.save()

    login(driver, test_username=user_data['root_username'],
          test_password=user_data['root_password'])

    logout(driver)

    return user_data


def test_signup(driver, django_db_blocker):
    user_data = signup(driver, django_db_blocker, username=str(uuid1()),
                       password=secrets.token_urlsafe(32),
                       email=f"{str(uuid1())}@tournesol.app")

    with django_db_blocker.unblock():
        DjangoUser.objects.filter(username=user_data['root_username']).delete()


def test_change_username(driver, django_db_blocker):
    login(driver)

    driver.find_element_by_id('personal_info_menu').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "edit_userprofile_button_id")))

    driver.find_element_by_id('edit_userprofile_button_id').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_change_username")))

    driver.find_element_by_id('id_change_username').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "root_username")))

    inp = driver.find_element_by_id('root_username')
    inp.clear()
    inp.send_keys('selenium_new_username')
    driver.find_element_by_id('change_login_name').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "login_button")))
    login(driver, test_username='selenium_new_username')

    driver.find_element_by_id('personal_info_menu').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "edit_userprofile_button_id")))

    driver.find_element_by_id('edit_userprofile_button_id').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_change_username")))

    assert driver.current_url.endswith('selenium_new_username')

    # reverting the username
    driver.find_element_by_id('id_change_username').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "root_username")))

    inp = driver.find_element_by_id('root_username')
    inp.clear()
    inp.send_keys(test_username)
    driver.find_element_by_id('change_login_name').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "login_button")))


def set_password(driver, newpass):
    driver.find_element_by_id('personal_info_menu').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "edit_userprofile_button_id")))

    driver.find_element_by_id('edit_userprofile_button_id').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_set_password")))

    driver.find_element_by_id('id_set_password').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "root_password")))

    p1 = driver.find_element_by_id('root_password')
    p2 = driver.find_element_by_id('root_password2')
    p1.clear()
    p2.clear()
    p1.send_keys(newpass)
    p2.send_keys(newpass)

    driver.find_element_by_id('id_set_password').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "login_button")))


def test_change_password(driver, django_db_blocker):
    login(driver)

    newpass = secrets.token_urlsafe(32)
    set_password(driver, newpass)

    login(driver, test_password=newpass)

    set_password(driver, test_password)


def test_password_reset(driver, django_db_blocker):
    open_tournesol(driver)

    # making my emails verified
    with django_db_blocker.unblock():
        ui = UserInformation.objects.get(user__username=test_username)
        ve = VerifiableEmail.objects.create(user=ui,
                                            email="selenium@test.com",
                                            is_verified=True)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "login_button")))

    driver.find_element_by_id('login_button').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_reset_password")))

    driver.find_element_by_id('id_reset_password').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_reset_submit")))

    username = driver.find_element_by_id('root_username')
    username.clear()
    username.send_keys(test_username)

    driver.find_element_by_id('id_reset_submit').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "id_email_instructions")))

    email_parsed = get_last_email()

    email_payload = None
    for payload in email_parsed.walk():
        email_payload = payload.get_payload()
    assert email_payload
    assert 'password reset' in email_payload
    print(email_payload)
    link = email_payload.strip().splitlines()
    link = [x for x in link if x.startswith(settings.EMAIL_PAGE_DOMAIN)][0].strip()
    print(link)
    link_no_domain = link[len(settings.EMAIL_PAGE_DOMAIN):]
    link_local_domain = web_url + '/' + link_no_domain
    driver.get(link_local_domain)

    print(link, link_no_domain, link_local_domain)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "root_password")))

    assert driver.find_element_by_id('root_password')

    logout(driver)

    with django_db_blocker.unblock():
        ve.delete()
