import secrets
from io import StringIO
from uuid import uuid1
import os

from backend.models import DjangoUser, EmailDomain
from django_react.settings import EMAIL_PAGE_DOMAIN, EMAIL_FILE_PATH, EMAIL_NEWDOMAIN_ADDRESS
from helpers import login, logout, web_url, random_alphanumeric, get_last_email, open_tournesol,\
    TIME_WAIT
from lxml import html
from test_signup import signup
import shutil
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def test_signup_verify_email(driver, django_db_blocker):
    # removing old emails
    shutil.rmtree(EMAIL_FILE_PATH)
    os.makedirs(EMAIL_FILE_PATH, exist_ok=True)

    with django_db_blocker.unblock():
        pending_domain = f"@{random_alphanumeric()}.com"
        accepted_domain = f"@{random_alphanumeric()}.com"
        rejected_domain = f"@{random_alphanumeric()}.com"
        # EmailDomain.objects.create(domain=pending_domain,
        #                            status=EmailDomain.STATUS_PENDING)
        EmailDomain.objects.create(domain=accepted_domain,
                                   status=EmailDomain.STATUS_ACCEPTED)
        EmailDomain.objects.create(domain=rejected_domain,
                                   status=EmailDomain.STATUS_REJECTED)

    signup(driver, django_db_blocker, username=random_alphanumeric(),
           password=secrets.token_urlsafe(32),
           email=f"test_first{pending_domain}")

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "signup_button")))

    two_last = [get_last_email(offset) for offset in [-1, -2]]
    two_last_from = [x.get('From', "") for x in two_last]
    assert any([x == EMAIL_NEWDOMAIN_ADDRESS for x in two_last_from]), two_last_from

    domains = {'pending': f"{random_alphanumeric()}{pending_domain}",
               'rejected': f"{random_alphanumeric()}{rejected_domain}",
               'accepted': f"{random_alphanumeric()}{accepted_domain}", }

    for email_type, email_address in domains.items():
        driver.get(web_url)

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, "signup_button")))

        # sign up
        driver.find_element_by_id('signup_button').click()

        password = secrets.token_urlsafe(32)
        user_data = {'root_username': str(uuid1()),
                     'root_email': email_address,
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
            EC.presence_of_element_located((By.ID, "button_home_page_to_verify_id")))

        # going to the home page
        driver.find_element_by_id('button_home_page_to_verify_id').click()

        email_parsed = get_last_email()

        email_payload = None
        for payload in email_parsed.walk():
            if payload.get_content_type() == 'text/html':
                email_payload = payload.get_payload()
        assert email_payload

        html_parsed = html.parse(StringIO(email_payload))

        assert html_parsed.xpath("//p[@id = 'confirmation_text_id']")

        for email_other_type in domains.keys():
            items = html_parsed.xpath(f"//*[@id = 'email_{email_other_type}_id']")
            if email_other_type == email_type:
                assert items
            else:
                assert not items, (email_type, email_other_type, email_payload, email_address)

        # confirming e-mail address
        confirm_link = html_parsed.xpath("//a[@id = 'confirmation_link_id']")[0].get('href')
        confirm_link = confirm_link.replace(EMAIL_PAGE_DOMAIN, 'http://127.0.0.1:8000/')
        print("Navigating to", confirm_link)
        driver.get(confirm_link)

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, "button_home_page_verified_id")))

        # going to the home page
        driver.find_element_by_id('button_home_page_verified_id').click()

        open_tournesol(driver)

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, "login_button")))

        login(driver, test_username=user_data['root_username'],
              test_password=user_data['root_password'])

        logout(driver)

        with django_db_blocker.unblock():
            DjangoUser.objects.filter(username=user_data['root_username']).delete()
