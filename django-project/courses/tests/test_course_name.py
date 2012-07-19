from django.test import TestCase
from c2g.models import Institution, Course
from django.contrib.auth.models import Group 
from django.template.loader import render_to_string
from db_test_data.management.commands.db_populate import Command 

class SimpleTest(TestCase):

    course_prefix="nlp"
    course_suffix="fall2012"
    course_name="Natural Language Processing"
    course_title_search_string="<h2>"+course_name+"</h2>"

    # Database setup
    pop_command = Command()
    def setUp(self):
        self.pop_command.handle()
    def tearDown(self):
        pass

    def render_and_check_template(self, templ):
        "Render a template and see if the course title is in a header element."
        try:
            course = Course.objects.get(handle=self.course_prefix+"-"+self.course_suffix)
        except:
            self.fail("Couldn't lookup test course")
        template_vars= {'course_prefix': self.course_prefix, 
                'course_suffix': self.course_suffix, 
                'course': course}
        page = render_to_string(templ, template_vars)
        self.assertRegexpMatches(page, self.course_title_search_string, msg="Couldn't find course header (%s) in %s" % (self.course_title_search_string, templ))

    # Test Cases

    def test_course_title_homepage(self):
        "Iterate through all templates and test each one"
        targets = ['courses/view.html'] 
        for templ in targets:
            self.render_and_check_template(templ)
        
