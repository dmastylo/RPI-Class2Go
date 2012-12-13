import unittest
from test_harness.test_base import AuthenticatedTestBase

__all__ = ['test_standalone', 'InstructorDraftModeTest']

def test_standalone():
    """
    Tests standalone function inclusion
    """
    pass

class InstructorDraftModeTest(AuthenticatedTestBase):

    def __init__(self, *arrgs, **kwargs):
        config = { 'username' : 'professor_0',
                   'password' : 'class2go',
                   'course_prefix' :'networking',
                   'course_suffix' :'Fall2012',
                   'mode' : 'draft' }
        if kwargs != None:
            kwargs.update(config)
        else:
            kwargs = config
        super(InstructorDraftModeTest, self).__init__(*arrgs, **kwargs)

    @unittest.skip('this is obsolete with the landing of exams')
    def test_basic_page_access(self):
        """
        Tests that we can access the basic test problem set pages
        url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/
               problemsets/(?P<pset_slug>[a-zA-Z0-9_-]+)?$',
            'problemsets.views.show'),
        """

        # load the normal problem set page
        resp = self.client.get('/networking/Fall2012/problemsets/P2', HTTP_USER_AGENT=self.userAgent)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('pset_url' in resp.context)
        self.assertEqual(resp.context['pset_url'], '/networking/Fall2012/problemsets/P2/load_problem_set')

    @unittest.skip('this is obsolete with the landing of exams')
    def test_pset_load(self):
        """
        Tests that we can load the actual problem set 
        url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/
               problemsets/(?P<pset_slug>[a-zA-Z0-9_-]+)/
               load_problem_set?$', 'problemsets.views.load_problem_set'),
        """
        # load a page with just the problem set
        resp = self.client.get('/networking/Fall2012/problemsets/P2/load_problem_set', HTTP_USER_AGENT=self.userAgent)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('file_names' in resp.context)
        self.assertEqual(resp.context['file_names'][0], 'xx_P2_Lexical1')

    @unittest.skip('this is obsolete with the landing of exams')
    def test_load_all_psets(self):
        """
        Tests the view all problemset page
        url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/
               problemsets/?$',
            'problemsets.views.listAll'),
        """
        resp = self.client.get('/networking/Fall2012/problemsets/', HTTP_USER_AGENT=self.userAgent)
        self.assertEqual(resp.status_code, 200)

    @unittest.skip('this is obsolete with the landing of exams')
    def test_load_manage_exercises(self):
        """
        Tests the loading of the problemset manage exercises page
        url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/
               problemsets/(?P<pset_slug>[a-zA-Z0-9_-]+)/
               manage_exercises?$',
            'problemsets.views.manage_exercises'),
        """
        resp = self.client.get('/networking/Fall2012/problemsets/P2/manage_exercise', HTTP_USER_AGENT=self.userAgent)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['exercises']), 2)

    @unittest.skip('this is obsolete with the landing of exams')
    def test_create_problemset_page(self):
        """
        Tests the display of the problemset creation page
        url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/
              createproblemset/?$',
            'problemsets.views.create_form'),
        """
        resp = self.client.get('/networking/Fall2012/createproblemset/', HTTP_USER_AGENT=self.userAgent)
        self.assertEqual(resp.status_code, 200)

