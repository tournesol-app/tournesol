import datetime
import email
import os
import string
import sys
from functools import partial
from io import BytesIO
from json import JSONDecodeError
from time import time, sleep
from uuid import uuid1

import django

sys.path.insert(0, os.path.abspath('../backend/'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_react.settings'
django.setup()

import cv2  # noqa: E402
import numpy as np  # noqa: E402
import shortuuid  # noqa: E402
from PIL import Image  # noqa: E402
from backend.models import Video  # noqa: E402
from backend.rating_fields import VIDEO_FIELDS  # noqa: E402
from django_react.selenium_config import SELENIUM_USERNAME, SELENIUM_PASSWORD  # noqa: E402
from django_react.settings import EMAIL_FILE_PATH  # noqa: E402
from requests import get  # noqa: E402
from selenium import webdriver  # noqa: E402
import geckodriver_autoinstaller  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.common.exceptions import NoSuchElementException  # noqa: E402

# automatically install geckodriver
geckodriver_autoinstaller.install()

# constants
web_url = 'http://127.0.0.1:8000'
test_username = SELENIUM_USERNAME
test_password = SELENIUM_PASSWORD
# time to wait in seconds for any action to complete
TIME_WAIT = 10
ENABLE_IMAGES = os.environ.get('SELENIUM_ENABLE_IMAGES', None) is not None


def element_present_now(driver, elem_id):
    """True iff element is now present."""
    try:
        driver.find_element_by_id(elem_id)
        return True
    except NoSuchElementException:
        return False


def open_more_menu(driver):
    """Open the MORE menu."""

    # waiting for the menu
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_menu_all')))

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'more_button')))

    # if already open, do nothing
    if not element_present_now(driver, 'id_more_open'):
        driver.find_element_by_id('more_button').click()

        WebDriverWait(driver, TIME_WAIT).until(
            EC.visibility_of_element_located((By.ID, 'id_list_more')))

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_more_open')))


def close_more_menu(driver):
    """Close the MORE menu."""

    # waiting for the menu
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, 'id_menu_all')))

    # if already closed, do nothing
    if not element_present_now(driver, 'id_more_closed'):
        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'more_button')))

        driver.find_element_by_id('more_button').click()

        WebDriverWait(driver, TIME_WAIT).until(
            EC.invisibility_of_element_located((By.ID, 'id_list_more')))

        WebDriverWait(driver, TIME_WAIT).until(
            EC.presence_of_element_located((By.ID, 'id_more_closed')))


def random_alphanumeric(length=10, alphabet=None):
    """UUID1 without -."""
    if alphabet is None:
        alphabet = string.ascii_lowercase + string.digits
    res = shortuuid.ShortUUID(alphabet=alphabet).random(length=length)
    return str(res).replace('-', '')


def get_cookies(driver):
    """Get auth cookies (useful for API calls)."""
    cookies = driver.get_cookies()
    cookies_dict = {x['name']: x['value'] for x in cookies}
    return cookies_dict


def get_object_with_timeout(model, timeout=TIME_WAIT, delay=0.01, get=True,
                            min_count=1, **kwargs):
    """Get an object from a model, or None."""
    started = time()
    while time() - started <= timeout:
        qs = model.objects.filter(**kwargs)

        if qs.count() >= min_count:
            if get:
                if qs.count() == 1:
                    return qs.get()
                elif qs.count() > 1:
                    raise ValueError(f"Query {model} {kwargs} returned too many items {qs.count()}")
            else:
                return qs
        sleep(delay)
    raise ValueError(f"Query {model} {kwargs} returned no items in {timeout} seconds")


def filter_object_with_timeout(model, timeout=TIME_WAIT, min_count=1,
                               delay=0.01, **kwargs):
    """Filter objects from a model, or None."""
    return get_object_with_timeout(model=model, timeout=timeout,
                                   min_count=min_count,
                                   get=False,
                                   delay=delay, **kwargs)


def do_api_call_stub(driver, url, method=get, base="", expect_fail=False,
                     cookie_auth=True, **kwargs):
    """Do Tournesol API call."""
    print("API call", base, url, method, kwargs)
    assert url.startswith('/'), f"API call URLs must start with /, got {url}"
    url = web_url + base + url
    cookies_dict = {}
    if cookie_auth:
        cookies_dict = get_cookies(driver)
        kwargs['headers'] = {'X-CSRFToken': cookies_dict.get('csrftoken')}
        kwargs['cookies'] = cookies_dict
    r = method(url, **kwargs)

    if expect_fail:
        return r
    else:
        assert r.ok, f"Request failed {driver} {cookies_dict} {url} {method} {kwargs}" \
                     f" {r.status_code} {r.text}"
        print(f"API call {url} returned OK")
        try:
            return r.json()
        except JSONDecodeError as e:
            print("Can't decode json:", r.text)
            raise e


do_api_call_v2 = partial(do_api_call_stub, base='/api/v2')


def set_slider_value(driver, value, slider=None, s_id=""):
    """Set value of a slider, input: 0-100."""
    print(f"Set value of slider {s_id} to {value}")
    if slider is None:
        slider = driver.find_element_by_id(s_id)
    y = (slider.rect['width'] - 1) * value / 100
    slider.click()
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(slider, y, slider.rect['height'] / 2)
    action.click()
    action.perform()


class DriverWithScreenshot(object):
    """Take screenshots at every getattr()."""

    def __init__(self, driver, enable_images=ENABLE_IMAGES):
        """Save the initial driver."""
        self.driver = driver
        self._enable_images = enable_images
        self._out_filename = f"integration_test_{str(uuid1())}.avi"

        # list of screenshots
        self._images = []

    def _capture_screenshot(self):
        """Capture one screenshot if it is different."""
        if not self._enable_images:
            return
        img_png = self.driver.get_screenshot_as_png()
        if self._images and self._images[-1] == img_png:
            print("Already have the image")
            return
        print("Adding the image")
        self._images.append(img_png)

    def _write_screenshots(self):
        """Write screenshots (at the end)."""
        if not self._enable_images:
            return

        def png2mat(png):
            return Image.open(BytesIO(png))

        if not self._images:
            print("There are no screenshots")
            return

        size = png2mat(self._images[0]).size
        print("Size", size)

        out = cv2.VideoWriter(self._out_filename, cv2.VideoWriter_fourcc(*'DIVX'), 2, size)

        for img in self._images:
            pil_image = png2mat(img).convert('RGB')

            open_cv_image = np.array(pil_image)
            # Convert RGB to BGR
            open_cv_image = open_cv_image[:, :, ::-1].copy()

            out.write(open_cv_image)
        out.release()

        print(f"Your video is in {self._out_filename}")

    def __getattribute__(self, attr_name):
        """Redirect request to self.driver or return a function from this class."""
        # print('Getattr', attr_name)
        whitelist = ['close']

        def get_from_self():
            return object.__getattribute__(self, attr_name)

        if attr_name == 'driver':
            return get_from_self()

        if attr_name.startswith('_') or attr_name in whitelist:
            return get_from_self()

        self._capture_screenshot()
        return object.__getattribute__(self.driver, attr_name)

    def __setattribute__(self, attr_name, value):
        """Set attribute override."""
        object.__setattribute__(self.driver, attr_name, value)

    def close(self):
        """Write screenshots on close."""
        self._write_screenshots()
        self.driver.close()
        self.driver = None


def get_driver():
    """Get driver (Firefox)."""
    print("Creating driver")
    driver = webdriver.Firefox()
    # driver = webdriver.Chrome()
    driver.maximize_window()
    driver = DriverWithScreenshot(driver)
    return driver


def close_driver(driver):
    """Tear down the driver."""
    print("Closing the driver")
    driver.close()


def open_tournesol(driver):
    """Open Tournesol local development website."""
    print("Opening tournesol")
    driver.delete_all_cookies()
    driver.get("about:blank")
    driver.get(web_url)
    assert 'Tournesol' in driver.title


def login(driver, test_username=test_username, test_password=test_password):
    """Log in to tournesol."""

    open_tournesol(driver)

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "login_button")))

    print("Opening login page")
    login_button = driver.find_element_by_id('login_button')
    login_button.click()

    print("Typing in data")
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "root_username")))
    username = driver.find_element_by_id('root_username')
    username.clear()
    username.send_keys(test_username)
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "root_password")))
    password = driver.find_element_by_id('root_password')
    password.clear()
    password.send_keys(test_password)

    print("Logging in")
    do_login = driver.find_element_by_id('submit-id-submit')
    do_login.click()

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "logout_button")))

    assert driver.title.startswith('Tournesol')


def logout(driver):
    """Log out from tournesol."""
    print("Logout...")
    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "logout_button")))
    logout_button = driver.find_element_by_id('logout_button')
    logout_button.click()

    assert 'Tournesol' in driver.title

    WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.ID, "login_button")))

    login_button = driver.find_element_by_id('login_button')
    assert login_button


def create_test_video(name="test name"):
    video_id = shortuuid.ShortUUID().random(length=10)

    v = Video.objects.create(video_id=video_id, name=name, views=100,
                             publication_date=datetime.datetime.now(),
                             duration=datetime.timedelta(seconds=60))
    for k in VIDEO_FIELDS:
        setattr(v, k, 50)
    v.save()
    return video_id


def get_last_email(offset=-1):
    """Return last e-mail from django, requires file backend."""
    # adding an e-mail
    # loading latest e-mail

    email_files = sorted(filter(lambda x: x.endswith('.log'), os.listdir(EMAIL_FILE_PATH)))
    try:
        email_file = email_files[offset]
    except IndexError:
        return {}
    email_path = os.path.join(EMAIL_FILE_PATH, email_file)

    print("Log found", email_path)

    with open(email_path, 'rb') as f:
        email_parsed = email.message_from_bytes(f.read())

    return email_parsed
