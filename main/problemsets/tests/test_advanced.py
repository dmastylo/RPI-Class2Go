from django.test import TestCase
from c2g.models import Course, ProblemSet
from problemsets.tests.test_base import SimpleTestBase

class AdvancedDraftModeTest(SimpleTestBase):
    fixtures = ['pset_testdata.json']
    username = 'professor_0'
    password = 'class2go'
    coursePrefix = 'networking'
    courseSuffix = 'Fall2012'

    def test_create_problemset_page(self):
        """
        Test the display of the problemset creation page
        url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/
              createproblemset/?$',
            'problemsets.views.create_form'),
        """
        resp = self.client.get('/networking/Fall2012/createproblemset/' )
        self.assertEqual(resp.status_code, 200)

    def test_create_problemset_action(self):
        """
        Test the actual creation of a new problemset
        url(r'^createproblemsetaction/?',
            'problemsets.views.create_action'),
        """
        # Get the number of problemsets
        numProblemSets = len(ProblemSet.objects.all())
        self.assertEqual(numProblemSets,4)

        # Create a new problemset
        resp = self.client.post('/networking/Fall2012/createproblemsetaction/' )

        # assert that we got redirected to the manage_exercises page
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'], 'http://testserver/networking/Fall2012/problemsets/P2/manage_exercise')

        # assert that there is one more problemset
        self.assertEqual(len(ProblemSet.objects.all()), numProblemSets+1)


    # More problemset urls to handle - look these up to find out what they are supposed to do.
    # url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/problemsets/(?P<pset_slug>[a-zA-Z0-9_-]+)/edit/?$',
    #     'problemsets.views.edit_form'),
    # url(r'^editproblemsetaction/?',
    #     'problemsets.views.edit_action'),
    # url(r'^add_existing_problemset_exercises/?$',
    #     'problemsets.views.add_existing_exercises'),
    # url(r'^save_problemset_exercises/?',
    #     'problemsets.views.save_exercises'),
    # url(r'^delete_exercise/?',
    #     'problemsets.views.delete_exercise'),
    # url(r'^delete_problemset/?',
    #     'problemsets.actions.delete_problemset'),
    # url(r'^(?P<course_prefix>[a-zA-Z0-9_-]+)/(?P<course_suffix>[a-zA-Z0-9_-]+)/exercises/(?P<exercise_name>.+)$',
    #     'problemsets.views.read_exercise'),
    # url(r'^problemsets/attempt/(?P<problemId>\d+)/?$',
    #     'problemsets.views.attempt'),
    # url(r'^problemsets/attempt_protect/(?P<problemId>\d+)/?$',
    #     'problemsets.views.attempt_protect'),

