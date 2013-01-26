from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from nose.plugins.attrib import attr
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0

from os import environ

if ( environ.has_key('C2G_HEADLESS_TESTS') and
     environ['C2G_HEADLESS_TESTS'] ):
  from pyvirtualdisplay import Display

class SeleniumTestBase(LiveServerTestCase):

    @classmethod
    def setup_class(cls):
        if ( environ.has_key('C2G_HEADLESS_TESTS') and
             environ['C2G_HEADLESS_TESTS'] ):
            cls.display = Display(visible=0, size=(800, 600))
            cls.display.start()
        cls.browser = webdriver.Chrome()
        super(SeleniumTestBase, cls).setUpClass()

    @classmethod
    def teardown_class(cls):
        cls.browser.quit()
        if ( environ.has_key('C2G_HEADLESS_TESTS') and
             environ['C2G_HEADLESS_TESTS'] ):
            cls.display.stop()
        super(SeleniumTestBase, cls).tearDownClass()

    def do_login(self):
        """
        Login in to the site with the preset username & password.
        """
        browser = self.browser

        # fetch the page and make sure it loads and we have a user entry field
        browser.get('%s%s' % (self.live_server_url, self.login_path))

        print(self.live_server_url)

        WebDriverWait(browser, 10).until(lambda browser : browser.find_element_by_id('id_username'))

        # now that we have the page, fill out the form
        userField = browser.find_element_by_id('id_username')
        userField.send_keys(self.username)
        passField = browser.find_element_by_id('id_password')
        passField.send_keys(self.password)

        # trigger the form submission
        inputEle = browser.find_element_by_xpath('//input[@type="submit"]')
        inputEle.submit()

        # wait at most 10 seconds or until we see evidence of login
        WebDriverWait(browser, 10).until(lambda browser : browser.find_element_by_xpath('//span[contains(text(), "Welcome")]'))


class StudentBase(SeleniumTestBase):
    """
    A class that defines the configurable data needed to target a specific
    course for a specific user.
    """
    fixtures = ['db_snapshot_video_tests.json']
    login_path = '/accounts/login'
    course_prefix = 'networking'
    course_suffix = 'Fall2012'
    course_name = 'Natural Language Processing'
    username = 'student_1'
    user_type = 'student'
    password = 'class2go'

class InstructorBase(SeleniumTestBase):
    """
    A class that defines the configurable data needed to target a specific
    course for a specific user.
    """
    fixtures = ['db_snapshot_video_tests.json']
    login_path = '/accounts/login'
    course_prefix = 'networking'
    course_suffix = 'Fall2012'
    course_name = 'Natural Language Processing'
    username = 'professor_0'
    user_type = 'instructor'
    password = 'class2go'


