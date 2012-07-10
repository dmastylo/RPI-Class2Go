"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from c2g.models import Institution, Course
from django.contrib.auth.models import Group 

class C2GUnitTests(TestCase):
    fixtures = ['db_snapshot.json']
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_index_page(self):
        """
        Tests that we can access the index page
        """
        resp=self.client.get('/')
        self.assertEqual(resp.status_code,200)

    def test_course_create(self):
        """
        Tests that course creation creates groups
        """
        numGroupsB4=len(Group.objects.all())
        i=Institution(title='TestInstitute')
        i.save()
        course1=Course(institution=i,title='gack',handle='test-course')
        course1.save()
        numGroupsAfter=len(Group.objects.all())
        self.assertEqual(numGroupsB4+4, numGroupsAfter)