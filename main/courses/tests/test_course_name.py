from django.test import TestCase
from c2g.models import Institution, Course
from django.contrib.auth.models import Group, AnonymousUser
from db_test_data.management.commands.db_populate import Command 
from django.test.client import RequestFactory  
import courses.views
import courses.videos.views
import problemsets.views

class SimpleTest(TestCase):

    course_prefix="networking"
    course_suffix="Fall2012"
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

    def request_and_search(self, viewname):
        request = self.factory.get(self.course_url)
        request.user = AnonymousUser()
        request.session = {}
        response = viewname(request, self.course_prefix, self.course_suffix)
        self.assertRegexpMatches(response.content, 
                self.course_title_search_string,
                msg="Couldn't find course name in from view '%s'" % viewname.__name__)

    def test_coursename_header_for_course_views(self):
        self.request_and_search(courses.views.main)
        self.request_and_search(courses.views.overview)
        self.request_and_search(courses.views.syllabus)

    def test_coursename_header_for_video_views(self):
        self.request_and_search(courses.videos.views.list)

    def test_coursename_header_for_problemset_views(self):
        self.request_and_search(problemsets.views.list)
