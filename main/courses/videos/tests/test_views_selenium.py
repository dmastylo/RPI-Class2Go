from django.core.urlresolvers import reverse
from lxml import etree
from nose.plugins.attrib import attr
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from test_harness.test_base_selenium import InstructorBase, StudentBase


def DEBUG(s):
    """A useful method for adding tracing to help figure out why tests go bad

    Particularly helpful for working with remote test services that capture
    output, like travis-ci."""
    import sys
    sys.stderr.write(s)


class InstructorVideoTest(InstructorBase):

    @attr('selenium')
    @attr(user='instructor')
    def test_course_video_problem_set(self):
        """[sel] Test an instructor can load and display a video problemset"""
        # log in to the site before loading a page
        self.do_login()
        browser = self.browser

        # load the problem set for video 4
        list_url = reverse('course_video_pset',
                           kwargs={'course_prefix' : self.course_prefix,
                                   'course_suffix' : self.course_suffix,
                                   'video_id' : 4 })
        browser.get('%s%s' % (self.live_server_url, list_url))
        WebDriverWait(browser, 15).until(lambda browser : browser.find_element_by_xpath('//body'))

        # make sure we have an exercise div
        self.assertTrue(browser.find_element_by_xpath('//div[contains(@class, "exercise")]'))
        # pull the data-name attributes from exercise divs
        tree = etree.HTML(browser.page_source)
        result = tree.xpath('//div[contains(@class, "exercise")]/@data-name')
        # check that we got the right number of exercises - TODO: use the ORM to get the count
        self.assertEqual(len(result), 1, msg="Unexpected number of divs with data.")
        # check that we got the right exercise - TODO: use the ORM to get the name
        self.assertEqual('xx_P1_Regexp', result[0])


class StudentVideoTest(StudentBase):

    @attr('selenium')
    @attr(user='student')
    def test_course_video(self):
        """[sel] Tests that a student can display an individual video"""
        self.do_login()
        browser = self.browser

        # get the list of videos
        list_url = reverse('course_video_list',
                           kwargs={'course_prefix' : self.course_prefix,
                                   'course_suffix' : self.course_suffix })
        browser.get('%s%s' % (self.live_server_url, list_url))
        WebDriverWait(browser, 15).until(lambda browser : browser.find_element_by_xpath('//body'))

        # pull the urls of each video from the in-page list
        tree = etree.HTML(browser.page_source)
        # pull the href from the anchor contained in the course-list-content
        urls = tree.xpath('//div[@class="course-list-content"]//a/@href')
        self.assertEqual(len(urls), 3, msg="Wrong number of live videos.")

        url = urls[1]   # An essentially random, yet reproducible, choice
        browser.get('%s%s' % (self.live_server_url, url))
        # When loaded we should have an iframe that contains the youtube content
        WebDriverWait(browser, 15).until(lambda browser : browser.find_element_by_tag_name('iframe'))
        # switch to the iframe for the youtube player and find the embeded player
        browser.switch_to_frame(browser.find_element_by_tag_name('iframe'))
        self.assertTrue(browser.find_element_by_xpath('//embed[@id="video-player"]'))

