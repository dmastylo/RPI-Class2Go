from django.core.urlresolvers import reverse
from lxml import etree
from nose.plugins.attrib import attr
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from test_base_selenium import SeleniumTestBase

import ipdb

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
            browser.switch_to_frame('player')
            self.assertTrue(browser.find_element_by_xpath('//embed[@id="video-player-flash"]'))
