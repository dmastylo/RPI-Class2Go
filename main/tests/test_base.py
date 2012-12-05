from django_nose import FastFixtureTestCase

__all__ = ['SimpleTestBase']

class SimpleTestBase(FastFixtureTestCase):
    fixtures = ['db_snapshot.json']

    def setUp(self):
        pass

    def tearDown(self):
        pass

class AuthenticatedTestBase(SimpleTestBase):
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
    loginPath = '/%s/%s/preview_login/'
    userAgent = 'Mozilla/5.0'
    referer = 'http://testserver/%s/%s/preview/'

    # the following are specific to each TestCase subclass and should be
    # passed in to __init__
    username = None
    password = None
    coursePrefix = None
    courseSuffix = None
    mode = None

    def __init__(self, *args, **kwargs):
        """
        Expects to receive the following args passed in through kwargs:
          course_prefix
          course_suffix
          username
          password
          mode
        """
        assert 'course_prefix' in kwargs
        assert 'course_suffix' in kwargs
        assert 'username' in kwargs
        assert 'password' in kwargs
        assert 'mode' in kwargs

        self.coursePrefix = kwargs.pop('course_prefix', None)
        self.courseSuffix = kwargs.pop('course_suffix', None)
        self.username = kwargs.pop('username', None)
        self.password = kwargs.pop('password', None)
        self.mode = kwargs.pop('mode', None)
        super(SimpleTestBase,self).__init__(*args, **kwargs)

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

