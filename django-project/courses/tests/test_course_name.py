from django.test import TestCase
from c2g.models import Institution, Course
from django.contrib.auth.models import Group 
from db_test_data.management.commands.db_populate import Command 
from django.test.client import RequestFactory  
from courses.views import *

class SimpleTest(TestCase):

    course_prefix="nlp"
    course_suffix="fall2012"
    course_url="/"+course_prefix+"/"+course_suffix
    course_name="Natural Language Processing"
    course_title_search_string="<h2>"+course_name+"</h2>"

    # Database setup
    pop_command = Command()
    def setUp(self):
        self.pop_command.handle()
        self.factory = RequestFactory()

    def tearDown(self):
        pass

    def test_homepage_course_title(self):
        request = self.factory.get(self.course_url)
        response = view(request, self.course_prefix, self.course_suffix)
        self.assertRegexpMatches(response.content, 
                self.course_title_search_string,
                msg="Couldn't find name of course in the page")

