from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from nose.plugins.attrib import attr
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
#from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from lxml import etree

import ipdb

class C2GTestMixin():
    fixtures = ['db_snapshot_video_tests.json']
    login_path = '/preview/?login'
    course_prefix = 'networking'
    course_suffix = 'Fall2012'
    course_name="Natural Language Processing"
    username = 'professor_0'
    user_type = 'instructor'
    password = 'class2go'

class SeleniumTestBase(LiveServerTestCase, C2GTestMixin):

    @classmethod
    def setup_class(cls):
        cls.browser = ChromeWebDriver()
        #cls.browser = FirefoxWebDriver()
        cls.browser.implicitly_wait(3)
        super(SeleniumTestBase, cls).setUpClass()

    @classmethod
    def teardown_class(cls):
        cls.browser.quit()
        super(SeleniumTestBase, cls).tearDownClass()

    def do_login(self):
        browser = self.browser
        browser.get(self.live_server_url + '/' +
                    self.course_prefix + '/' +
                    self.course_suffix +
                    self.login_path)
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
        if self.user_type == 'instructor':
            WebDriverWait(browser, 10).until(lambda browser : browser.find_element_by_xpath('//span[contains(text(), "Welcome")]'))
        else:
            WebDriverWait(browser, 10).until(lambda browser : browser.find_element_by_xpath('//input[@type="hidden"][@name="csrfmiddlewaretoken"]'))

class SimpleDisplayTest(SeleniumTestBase):

    @attr('selenium')
    @attr(user='instructor')
    def test_load_networking(self):
        """
        [sel] Tests logging in to the networking class
        """
        self.do_login()
        browser = self.browser
        browser.get('%s%s' % (self.live_server_url, '/networking/Fall2012/'))
        WebDriverWait(browser, 10).until(lambda browser : browser.find_element_by_xpath('//title'))
        self.assertTrue(browser.find_element_by_xpath('//title[contains(text(), self.course_name)]'))

    @attr('selenium')
    @attr(user='instructor')
    def test_course_video_problem_set(self):
        """
        [sel] Tests the loading and display of a video problemset
        Is this a valid url to load directly?
        """
        # log in to the site before loading a page
        self.do_login()

        browser = self.browser
        list_url = reverse('course_video_pset',
                           kwargs={'course_prefix' : self.course_prefix,
                                   'course_suffix' : self.course_suffix,
                                   'video_id' : 4 })
        browser.get('%s%s' % (self.live_server_url, list_url))
        WebDriverWait(browser, 15).until(lambda browser : browser.find_element_by_xpath('//body'))

        self.assertTrue(browser.find_element_by_xpath('//div[contains(@class, "exercise")]'))
        tree = etree.HTML(browser.page_source)
        result = tree.xpath('//div[contains(@class, "exercise")]/@data-name')
        # check that we got the right number of exercises - TODO: use the ORM to get the count
        self.assertEqual(len(result), 1, msg="Unexpected number of divs with data.")
        # check that we got the right test - TODO: use the ORM to get the name
        self.assertEqual('xx_P1_Regexp', result[0])

class VideoDisplayTest(SeleniumTestBase):
    username = 'student_1'
    user_type = 'student'

    @attr(user='student')
    def test_course_video(self):
        """
        [sel] Tests the display of an individual video
        """
        self.do_login()
        browser = self.browser

        # check for the iframe with id=player and/or title=YouTube video player and/or src contains youtube.com
        # get the list of videos
        list_url = reverse('course_video_list',
                           kwargs={'course_prefix' : self.course_prefix,
                                   'course_suffix' : self.course_suffix })

        # fetch the page
        browser.get('%s%s' % (self.live_server_url, list_url))
        WebDriverWait(browser, 15).until(lambda browser : browser.find_element_by_xpath('//body'))

        # pull the urls of each video from the list
        tree = etree.HTML(browser.page_source)
        # pull the href from the anchor contained in the course-list-content
        urls = tree.xpath('//div[@class="course-list-content"]//a/@href')
        self.assertEqual(len(urls), 3, msg="Wrong number of live videos.")

        # attempt to load each video from the list
        for url in urls:
            browser.get('%s%s' % (self.live_server_url, url))
            # When loaded we should have a div to hold the YT content
            WebDriverWait(browser, 15).until(lambda browser : browser.find_element_by_xpath('//div[@id="player"]'))

            # switch to the iframe for the YT player
            ipdb.set_trace()
            browser.switch_to_frame('player')
            #tree = etree.HTML(browser.page_source)
            #player_divs = tree.xpath('//div[@id="player"]')
            #self.assertEqual(len(player_divs), 1)
            self.assertTrue(browser.find_element_by_xpath('//embed[@id="video-player-flash"]'))
