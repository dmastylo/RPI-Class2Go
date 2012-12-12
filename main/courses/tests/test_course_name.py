from django.core.urlresolvers import reverse
from test_harness.test_base import AuthenticatedTestBase

class SimpleTest(AuthenticatedTestBase):
    course_name="Natural Language Processing"

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
        super(SimpleTest, self).__init__(*arrgs, **kwargs)


    def test_course_main(self):
        """
        Tests the display of the main course page
        """
        response = self.client.get(reverse('course_main',
                                           kwargs={'course_prefix' : self.coursePrefix,
                                                   'course_suffix' : self.courseSuffix }),
                                   HTTP_USER_AGENT=self.userAgent)
        self.assertEqual(response.status_code, 200)

        course_title_search_string = "<h2>" + self.course_name + "</h2>"
        self.assertRegexpMatches(response.content, 
                course_title_search_string,
                msg="Couldn't find course name in '%s'" % reverse('course_main',
                                           kwargs={'course_prefix' : self.coursePrefix,
                                                   'course_suffix' : self.courseSuffix }))

    def test_course_materials(self):
        """
        Tests the display of course materials
        """
        response = self.client.get(reverse('course_materials',
                                           kwargs={'course_prefix' : self.coursePrefix,
                                                   'course_suffix' : self.courseSuffix }),
                                   HTTP_USER_AGENT=self.userAgent)
        self.assertEqual(response.status_code, 200)

        course_title_search_string = self.course_name + "</title>"
        self.assertRegexpMatches(response.content, 
                course_title_search_string,
                msg="Couldn't find course name in '%s'" % reverse('course_materials',
                                           kwargs={'course_prefix' : self.coursePrefix,
                                                   'course_suffix' : self.courseSuffix }))

