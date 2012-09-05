"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from c2g.models import Course, ProblemSet

class SimpleTest(TestCase):
    fixtures = ['pset_testdata.json']

    def test_fixure_loading(self):
        """
        Tests the fixture loaded correctly
        """
        numCourse = len(Course.objects.all())
        self.assertEqual(numCourse,1)
    def test_basic_pageAccess(self):
        """
        Tests that we can access the basic test problem set pages
        """
        resp = self.client.get('/nlp/draft/problemsets/P1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('pset_url' in resp.context)
        self.assertEqual(resp.context['pset_url'], '/static/latestKhan/exercises/P1.html')