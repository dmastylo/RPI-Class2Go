from django.test import TestCase
from c2g.models import Institution, Course
from courses.common_page_data import get_common_page_data
from django.contrib.auth.models import Group, AnonymousUser, User
from db_test_data.management.commands.db_populate import Command 
from django.test.client import RequestFactory, Client
import courses.views
import courses.videos.views
import problemsets.views

class SimpleTest(TestCase):
    fixtures=['db_snapshot.json']

    course_prefix="networking"
    course_suffix="Fall2012"
    course_url="/"+course_prefix+"/"+course_suffix
    course_name="Natural Language Processing"
    course_title_search_string="<h2>"+course_name+"</h2>"

    # Database setup
    pop_command = Command()
    def setUp(self):
        self.user = User.objects.get(username="professor_1")
        self.pop_command.handle()
        self.factory = RequestFactory()
        self.client = Client()

    def tearDown(self):
        pass

    def request_and_search(self, viewname):
        # import pdb; pdb.set_trace();
        request = self.factory.get(self.course_url)
        # TODO - not working
        request.user = self.client.login(username="professor_1", password="class2go")
        request.common_page_data=get_common_page_data(request, 
                self.course_prefix, self.course_suffix)
        request.session = {}
        response = viewname(request, self.course_prefix, self.course_suffix)
        self.assertRegexpMatches(response.content, 
                self.course_title_search_string,
                msg="Couldn't find course name in from view '%s'" % viewname.__name__)

    def test_coursename_header_for_course_views(self):
        self.request_and_search(courses.views.main)
        self.request_and_search(courses.views.overview)
        self.request_and_search(courses.views.syllabus)
        self.request_and_search(courses.videos.views.list)
        self.request_and_search(problemsets.views.list)

