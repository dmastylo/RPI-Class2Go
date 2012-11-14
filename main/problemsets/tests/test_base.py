from django.test import TestCase
from django_nose import FastFixtureTestCase

__all__ = ['SimpleTestBase']

class SimpleTestBase(FastFixtureTestCase):
    """
    A base class for test classes that need to log in to the system and
    switch to edit mode to ensure access to the correct data.

    For each test method the urls from the main urls.py file has been included.
    If those urls change and these tests break be sure to update the comment
    as well as the test.

    TODO: If needed, parameterize each step so that some tests can log
          in only and stay in draft mode.
          Also provide configuration for the u/p (to allow student logins)
          Perhaps even take the path and parse it for the pre/suf
    """
    mode = 'draft'
    loginPath = '/%s/%s/preview_login/'
    userAgent = 'Mozilla/5.0'
    referer = 'http://testserver/%s/%s/preview/'

    # XXXredfive - Make the inheritance work
    # tried using __init__ to set these but there is something wonky with
    # the inheritance; letting the subclass override them for now
    username = 'set-me-in-subclass'
    password = 'set-me-in-subclass'
    coursePrefix = 'set-me-in-subclass'
    courseSuffix = 'set-me-in-subclass'

    def setUp(self):
        # login
        resp = self.client.post((self.loginPath%(self.coursePrefix,
                                                 self.courseSuffix)),
                                {'username' : self.username,
                                 'password' : self.password},
                                follow=True)
        self.assertEqual(resp.status_code, 200)

        # switch to edit mode for full access
        resp = self.client.post('/switch_mode/',
                                {'course_prefix': self.coursePrefix,
                                 'course_suffix': self.courseSuffix,
                                 'to_mode': self.mode},
                                HTTP_USER_AGENT=self.userAgent,
                                HTTP_REFERER=(self.referer%(self.coursePrefix,
                                                            self.courseSuffix)),
                                follow=True)
        self.assertEqual(resp.status_code, 200)

