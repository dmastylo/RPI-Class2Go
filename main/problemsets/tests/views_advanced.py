from c2g.models import ProblemSet
from problemsets.tests.test_base import SimpleTestBase
from datetime import datetime, timedelta

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

    #def test_create_problemset_action(self):
    #    """
    #    Test the actual creation of a new problemset
    #    url(r'^createproblemsetaction/?',
    #        'problemsets.views.create_action'),
    #
    #    currently required problemset data:
    #      'grace_period': [u'This field is required.'],
    #      'due_date': [u'This field is required.'],
    #      'submissions_permitted': [u'This field is required.'],
    #      'title': [u'This field is required.'],
    #      'late_penalty': [u'This field is required.'],
    #      'section': [u'This field is required.'],
    #      'resubmission_penalty': [u'This field is required.'],
    #      'assessment_type': [u'This field is required.'],
    #      'partial_credit_deadline': [u'This field is required.'],
    #      'slug': [u'This field is required.']
    #    """
    #    # Get the number of problemsets
    #    numProblemSets = len(ProblemSet.objects.all())
    #    self.assertEqual(numProblemSets,4)
    #
    #    # Create a new problemset
    #    resp = self.client.post('/createproblemsetaction/',
    #                            {'course_prefix': self.coursePrefix,
    #                             'course_suffix': self.courseSuffix,
    #                             'title': 'XXXXXXXXXX This is a test XXXXXXXX',
    #                             'slug':'newPS',
    #                             'assessment_type': 'formative',
    #                             'submissions_permitted': 5,
    #                             'late_penalty': 10,
    #                             'section': None,
    #                             'resubmission_penalty': 10,
    #                             'grace_period': datetime.strftime(datetime.today(), '%m/%d/%Y %H:%M'),
    #                             'partial_credit_deadline': datetime.strftime(datetime.today()+timedelta(21), '%m/%d/%Y %H:%M'),
    #                             'due_date':  datetime.strftime(datetime.today()+timedelta(7), '%m/%d/%Y %H:%M'),
    #                            },
    #                            HTTP_USER_AGENT=self.userAgent )
    #
    #
    #    # assert that we got redirected to the manage_exercises page
    #    self.assertEqual(resp.status_code, 302)
    #    self.assertEqual(resp['location'], 'http://testserver/networking/Fall2012/problemsets/P2/manage_exercise')
    #
    #    # assert that there is one more problemset
    #    self.assertEqual(len(ProblemSet.objects.all()), numProblemSets+1)


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

