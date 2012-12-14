import unittest
from c2g.models import ProblemSet
from datetime import datetime, timedelta
from test_harness.test_base import AuthenticatedTestBase

__all__ = ['InstructorDraftModeTestAdv']

class InstructorDraftModeTestAdv(AuthenticatedTestBase):

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
        super(InstructorDraftModeTestAdv, self).__init__(*arrgs, **kwargs)

    @unittest.skip('this is obsolete with the landing of exams')
    def test_create_problemset_action(self):
        """
        Tests the creation of a new problemset
        url(r'^createproblemsetaction/?',
            'problemsets.views.create_action'),
        """
        # Get the number of problemsets
        num_problem_sets = len(ProblemSet.objects.all())
        self.assertEqual(num_problem_sets, 4)
        self.assertEqual( len(ProblemSet.objects.filter(mode='ready')), num_problem_sets/2 )
        self.assertEqual( len(ProblemSet.objects.filter(mode='draft')), num_problem_sets/2 )
    
        # Create a new problemset
        resp = self.client.post('/createproblemsetaction/',
                                {'course_prefix': self.coursePrefix,
                                 'course_suffix': self.courseSuffix,
                                 'title': 'XXXXXXXXXX This is a test XXXXXXXX',
                                 'slug':'testPS',
                                 'assessment_type': 'formative',
                                 'submissions_permitted': 5,
                                 'late_penalty': 10,
                                 'section': '1',
                                 'resubmission_penalty': 10,
                                 'grace_period': datetime.strftime(datetime.today(), '%m/%d/%Y %H:%M'),
                                 'partial_credit_deadline': datetime.strftime(datetime.today()+timedelta(21), '%m/%d/%Y %H:%M'),
                                 'due_date':  datetime.strftime(datetime.today()+timedelta(7), '%m/%d/%Y %H:%M'),
                                },
                                HTTP_USER_AGENT=self.userAgent )

        # assert that we got redirected to the manage_exercises page
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'], 'http://testserver/networking/Fall2012/problemsets/testPS/manage_exercise')

        # assert that there are 2 more problemsets, one each for ready & draft
        self.assertEqual( len(ProblemSet.objects.all()), num_problem_sets+2 )
        self.assertEqual( len(ProblemSet.objects.filter(mode='ready')), (num_problem_sets/2)+1 )
        self.assertEqual( len(ProblemSet.objects.filter(mode='draft')), (num_problem_sets/2)+1 )

