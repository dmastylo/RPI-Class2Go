import datetime

from django.core.urlresolvers import reverse

from c2g.models import File as FileModel
from c2g.models import Course as CourseModel
from test_harness.test_base import AuthenticatedTestBase
from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile, FileField

class CourseMaterialsPageAndContentsTest(AuthenticatedTestBase):
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
        super(CourseMaterialsPageAndContentsTest, self).__init__(*arrgs, **kwargs)

    def setUp(self):
        super(CourseMaterialsPageAndContentsTest, self).setUp()
        self.course = CourseModel.objects.get(id=1)
        self.section = self.course.contentsection_set.all()[0]
        self.poorfile = FileModel(course=self.course, 
                                  section=self.section, 
                                  handle=self.course.handle, 
                                  live_datetime = datetime.datetime(9999, 12, 12, 1, 1, 1), 
                                  title="XXXDELETEMETESTXXX")
        self.poorfile.save()
        self.poorfile.create_ready_instance()
        self.poorfile.image.save()
	
        self.poorfile.file.save("NAMEME", ContentFile("hello world"), save=False)
        self.poorfile.save()
        self.poorfile.image.file.save("NAMEME", ContentFile("hello world"), save=False)
        self.poorfile.image.save()


    def tearDown(self):
        FileModel.objects.filter(title="XXXDELETEMETESTXXX").delete()
        super(CourseMaterialsPageAndContentsTest, self).tearDown()

    def test_course_materials_draft_with_futurefile(self):
        """
        Tests the display of course materials in draft mode with one nonlive file
        """
        response = self.client.get(reverse('course_materials',
                                           kwargs={'course_prefix' : self.coursePrefix,
                                                   'course_suffix' : self.courseSuffix }),
                                   follow=True,                      # Course Materials page always does redirect temporary
                                   HTTP_USER_AGENT=self.userAgent)   # exception handler throws exception if agent not set

        self.assertEqual(response.status_code, 200)

        course_title_search_string = self.course_name + "</title>"
        self.assertRegexpMatches(response.content, 
                course_title_search_string,
                msg="Couldn't find course name in '%s'" % reverse('course_materials',
                                           kwargs={'course_prefix' : self.coursePrefix,
                                                   'course_suffix' : self.courseSuffix }))

        not_live_search_string = "<span style='color:#A07000;'>Live 9999-12-12 at 01:01</span>"
        self.assertRegexpMatches(response.content, 
                                 not_live_search_string,
                                 msg="Couldn't find future date in '%s'" % reverse('course_materials',
                                                                           kwargs={'course_prefix' : self.coursePrefix,
                                                                                   'course_suffix' : self.courseSuffix }))

