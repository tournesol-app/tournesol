from helpers import web_url, login, logout, TIME_WAIT
from backend.models import EmailDomain
from uuid import uuid1
from contextlib import contextmanager
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def _test_domains(driver, ack_email, rej_email, pend_email):
    to_check = [(ack_email, 'accepted_domains_class')]

    for domain, elem_id in to_check:
        links = driver.find_element_by_class_name(elem_id).find_elements_by_class_name(
            'domain_link_class')
        print(links)
        global link
        link = links[0]
        print(dir(links[0]), links[0].text, links[0].tag_name, ack_email)
        assert any([link.text == domain for link in links])


@contextmanager
def _create_emails(django_db_blocker):
    ack_email = f"@{uuid1()}.com"
    rej_email = f"@{uuid1()}.org"
    pend_email = f"@{uuid1()}.io"

    # creating email domains
    with django_db_blocker.unblock():
        EmailDomain.objects.create(domain=ack_email, status=EmailDomain.STATUS_ACCEPTED)
        EmailDomain.objects.create(domain=rej_email, status=EmailDomain.STATUS_REJECTED)
        EmailDomain.objects.create(domain=pend_email, status=EmailDomain.STATUS_PENDING)

    yield ack_email, rej_email, pend_email

    # deleting email domains
    with django_db_blocker.unblock():
        EmailDomain.objects.filter(domain__in=[ack_email, rej_email, pend_email]).delete()


def test_withlogin(driver, django_db_blocker):
    login(driver)

    # going to user personal profile
    driver.find_element_by_id('personal_info_menu').click()

    # editing the profile

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'edit_userprofile_button_id')))

    driver.find_element_by_id('edit_userprofile_button_id').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'to_verified_domains_class')))

    # going to the list of domains
    driver.find_element_by_class_name('to_verified_domains_class').click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'domains')))

    with _create_emails(django_db_blocker) as domains:
        ack_email, rej_email, pend_email = domains
        driver.refresh()

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'domains')))

        _test_domains(driver, ack_email, rej_email, pend_email)

    logout(driver)


def test_nologin(driver, django_db_blocker):
    driver.get(web_url + '/email_domains')

    with _create_emails(django_db_blocker) as domains:
        ack_email, rej_email, pend_email = domains
        driver.refresh()
        _test_domains(driver, ack_email, rej_email, pend_email)

    driver.get(web_url)
